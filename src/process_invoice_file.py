import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import pdf2image
import pytesseract
from PIL import Image
import io
import os
from pdf2image import convert_from_path


TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
POPPLER_PATH = r'C:\Users\jason\OneDrive\Desktop\NUS Y3S2\Release-24.02.0-0\poppler-24.02.0\Library\bin'
DPI = 250

def pdf_to_images(pdfs_path):
    # Convert PDFs into images, one image per page
    for pdf_path in pdfs_path:
        images = pdf2image.convert_from_path(pdf_path, dpi=DPI, poppler_path=POPPLER_PATH)
    return images


def remove_lines(image):
    # Convert to grayscale and apply binary threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Define kernels for detecting horizontal and vertical lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
    
    # Detect lines
    detected_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    detected_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Combine lines
    combined_lines = cv2.addWeighted(detected_horizontal, 1.0, detected_vertical, 1.0, 0.0)
    
    # Subtract lines from the thresholded image
    thresh_without_lines = cv2.subtract(thresh, combined_lines)
    
    # Invert image back
    thresh_without_lines = cv2.bitwise_not(thresh_without_lines)

    return thresh_without_lines

# Enhance image quality after removing lines
def enhance_quality(image):
    # Initial denoising
    denoised_image = cv2.fastNlMeansDenoising(image, None, 30, 7, 21)
    
    # Adaptive thresholding for better text segmentation
    adaptive_thresh = cv2.adaptiveThreshold(denoised_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY, 11, 2)
    
    # Contrast enhancement
    yuv = cv2.cvtColor(adaptive_thresh, cv2.COLOR_GRAY2BGR)
    yuv = cv2.cvtColor(yuv, cv2.COLOR_BGR2YUV)
    yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
    contrast_enhanced_image = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
    contrast_enhanced_image = cv2.cvtColor(contrast_enhanced_image, cv2.COLOR_BGR2GRAY)
    
    # Sharpening
    sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    enhanced_image = cv2.filter2D(contrast_enhanced_image, -1, sharpen_kernel)


    return enhanced_image




import cv2
import pytesseract
from pytesseract import Output

def find_text_blobs(binary_image):
    # Invert the image for contour detection: white text on black background
    inverted_image = cv2.bitwise_not(binary_image)
    
    # Dilate to merge characters into blobs
    # Adjust the kernel size and iterations for dilation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 2))  # Wider kernel
    dilated = cv2.dilate(inverted_image, kernel, iterations=2)  # Fewer iterations

    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    blobs = []


    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        blobs.append({
            "coordinates": (x, y, w, h)
        })

    # Prepare for visualization: draw contours on the original inverted binary image
    output_image = cv2.cvtColor(inverted_image, cv2.COLOR_GRAY2BGR)  # Convert to BGR for colored drawing
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw in green
    
    # Note: Invert back if you wish to visualize with original background color
    # output_image = cv2.bitwise_not(output_image)
    
    return output_image, blobs



def extract_text_and_coordinates_from_image(image):
    # Check if the image is already in grayscale
    if len(image.shape) == 2 or image.shape[2] == 1:  # Grayscale images have 2 dimensions or 3rd dimension == 1
        gray_image = image  # The image is already grayscale
    else:
        # Convert to grayscale for better OCR results
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use pytesseract to extract text and bounding boxes
    details = pytesseract.image_to_data(gray_image, output_type=Output.DICT)
    
    texts_with_coordinates = []
    for i in range(len(details['text'])):
        if details['text'][i].strip() != '':
            x, y, w, h = details['left'][i], details['top'][i], details['width'][i], details['height'][i]
            texts_with_coordinates.append({"text": details['text'][i], "coordinates": (x, y, w, h)})

    # print(texts_with_coordinates)
    return texts_with_coordinates


def merge_texts_based_on_blobs(texts_with_coordinates, blobs, margin=10):
    """
    Merge texts based on proximity to blob bounding boxes with an added margin.

    Args:
    - texts_with_coordinates: List of dictionaries containing text and its coordinates.
    - blobs: List of dictionaries with 'coordinates' of blobs.
    - margin: Integer, pixels to expand the blob's bounding box for merging texts.

    Returns:
    - merged_texts: List of dictionaries with merged text and the original blob coordinates.
    """
    merged_texts = []
    for blob in blobs:
        blob_texts = []
        x1, y1, w1, h1 = blob['coordinates']

        # Expand blob's bounding box by margin
        expanded_x1 = x1 - margin
        expanded_y1 = y1 - margin
        expanded_x2 = x1 + w1 + margin
        expanded_y2 = y1 + h1 + margin

        for text_entry in texts_with_coordinates:
            x2, y2, w2, h2 = text_entry['coordinates']
            text_x_center = x2 + w2 / 2
            text_y_center = y2 + h2 / 2

            # Check if the center of text_entry is within or near the expanded blob's bounding box
            if expanded_x1 < text_x_center < expanded_x2 and expanded_y1 < text_y_center < expanded_y2:
                blob_texts.append(text_entry['text'])

        merged_text = " ".join(blob_texts)
        if merged_text:
            merged_texts.append({"text": merged_text, "coordinates": blob['coordinates']})

    return merged_texts


def visualize_text_on_image(image, texts_with_coordinates):
    """
    Display the grayscale image with bounding boxes and text.
    
    Args:
    - gray_image: Grayscale image as a numpy array.
    - texts_with_coordinates: List of dictionaries with "text" and "coordinates".
    """
    # Convert the grayscale image to BGR for colored annotations
    image_with_annotations = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    for item in texts_with_coordinates:
        text, (x, y, w, h) = item['text'], item['coordinates']
        
        # Draw bounding box in green
        cv2.rectangle(image_with_annotations, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Put extracted text in red above the bounding box
        cv2.putText(image_with_annotations, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, (0, 0, 255), 2)
    
    # # Visualization with Matplotlib (if desired)
    # import matplotlib.pyplot as plt

    # plt.figure(figsize=(10, 15))
    # plt.imshow(cv2.cvtColor(image_with_annotations, cv2.COLOR_BGR2RGB))
    # plt.axis('off')
    # plt.show()

    return image_with_annotations



# Assuming TESSERACT_PATH and other imports are defined above

def process_invoice_image(file_path, processed_folder):
    img = None  # Initialize img to None to handle the case where file_path is not a supported type

    # Determine if the file is a PDF or PNG
    if file_path.lower().endswith('.pdf'):
        images = convert_from_path(file_path, dpi=DPI, poppler_path=POPPLER_PATH) # May need to adjust dpi depending on the quality of image (could make it a parameter on web)
        if images:
            # Only process the first page
            image = images[0]
            img_np = np.array(image)  # Convert PIL image to numpy array
            img = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR
    elif file_path.lower().endswith('.png'):
        img = cv2.imread(file_path)

    if img is None:
        raise ValueError("Unsupported file type. Only PDF and PNG are supported.")

    # Continue processing the image as before
    processed_img = remove_lines(img)
    # enhanced_img = enhance_quality(processed_img)
    img_with_text_blobs, blobs = find_text_blobs(processed_img)
    text_coordinates_dict = extract_text_and_coordinates_from_image(processed_img)
    merged_texts = merge_texts_based_on_blobs(text_coordinates_dict, blobs)
    annotated_img = visualize_text_on_image(processed_img, merged_texts)

    # print(merged_texts)
    # Save the processed image to the processed_folder
    base_filename = os.path.basename(file_path)
    name, ext = os.path.splitext(base_filename)
    processed_filename = f"{name}_processed{ext}"
    # Ensure the processed file has a .png extension
    if not processed_filename.lower().endswith('.png'):
        processed_filename += '.png'  # Append .png extension if not present


    processed_path = os.path.join(processed_folder, processed_filename)
    
    cv2.imwrite(processed_path, annotated_img)

    return processed_path, blobs, merged_texts