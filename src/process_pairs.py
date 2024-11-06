import numpy as np

def calculate_distance(coord1, coord2):
    """
    Calculate Euclidean distance between two sets of coordinates (x1, y1, x2, y2).
    """
    return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)




import re

def sanitize_text(text):
    """
    Sanitizes the text by removing digits and extra whitespace.
    
    Args:
    - text: The original text string.
    
    Returns:
    - The sanitized text string.
    """
    # Remove digits
    text_no_digits = re.sub(r'\d+', '', text)
    # Remove special characters (if necessary) and strip extra whitespace
    sanitized_text = re.sub(r'[^\w\s]', '', text_no_digits).strip()
    return sanitized_text

from fuzzywuzzy import fuzz

def find_coordinates_by_text(text, merged_texts, dx, dy, label_variations=None, threshold=90, omit_text=None):
    """
    Finds the coordinates of a text in merged_texts using fuzzy string matching.
    Considers label variations if provided.

    Args:
    - text: The text to search for.
    - merged_texts: A list of dictionaries with 'text' and 'coordinates'.
    - dx, dy: Spatial relationship offsets. If both are 0, use fuzz.ratio.
    - label_variations: Optional; A dictionary of variations for the label text, where the key is the label and the value is a list of variations.
    - threshold: The minimum similarity score to consider a match.

    Returns:
    The coordinates of the best match if a suitable one is found above the threshold, otherwise None.
    """
    best_match_score = 0
    best_match_coordinates = None
    
    # If label_variations is a dict, extract the list of variations for the specific label
    variations_list = label_variations.get(text, []) if isinstance(label_variations, dict) else label_variations

    # Prepare a list of texts to check, including the original and any variations
    texts_to_check = [text] + variations_list
    print(texts_to_check)

    for entry in merged_texts:
        # Check for an exact match first
        if entry['text'] == text:
            return entry['coordinates'], entry['text']
        elif omit_text and entry['text'] == omit_text:
            continue
        for check_text in texts_to_check:
            if dx == 0 and dy == 0:
                original_length = len(check_text)
                cleaned_text = sanitize_text(check_text)
                cleaned_entry_text = sanitize_text(entry['text'])
                match_score = fuzz.partial_ratio(cleaned_text, cleaned_entry_text)
                length_similarity = abs(original_length - len(entry['text'])) <= len(check_text) * 0.1
            else:
                token_set_score = fuzz.token_set_ratio(check_text, entry['text'])
                ratio_score = fuzz.ratio(check_text, entry['text'])
                length_similarity = True
                match_score = max(token_set_score, ratio_score)

            if match_score > best_match_score and match_score >= threshold and length_similarity:
                best_match_score = match_score
                best_match_coordinates = entry['coordinates']
                best_match_text = entry['text']
                
    

    if best_match_coordinates:
        return best_match_coordinates, best_match_text
    else:
        return None, None
    







def find_closest_box(dx, dy, expected_coords, candidate_boxes, omit_box=None):
    """
    Find the closest box to the expected_coords among candidate_boxes.
    """

    min_distance = float('inf')
    distance = float('inf')
    closest_box = None
    for box in candidate_boxes:
        if dx == 0 and dy == 0:
            if (expected_coords[0], expected_coords[1]) == (box['coordinates'][0], box['coordinates'][1]):
                return box    
        if omit_box and box['coordinates'] == omit_box:
            continue
        elif abs(dx) > abs(dy):
            if dy == 0:
                dy = 1 # Set a small disturbance to avoid missing exact matches
            if abs(box['coordinates'][1] - expected_coords[1]) > (abs(dy) * 5):
                continue
            # elif (expected_coords[0] - dx, expected_coords[1] - dy) == (box['coordinates'][0], box['coordinates'][1]):
            #     continue
            print('Possible horizontal candidate: ' + box['text'])
            print('Expected coords: ' + str(expected_coords) + ' Box coords: ' + str(box['coordinates']))
            distance = calculate_distance(expected_coords, (box['coordinates'][0], box['coordinates'][1]))
        elif abs(dy) > abs(dx):
            if dx == 0:
                dx = 1 # Set a small disturbance to avoid missing exact matches
            if (abs(box['coordinates'][0]) - expected_coords[0]) > (abs(dx) * 5):
                continue
            # elif (expected_coords[0] - dx, expected_coords[1] - dy) == (box['coordinates'][0], box['coordinates'][1]):
            #     continue
            print('Possible vertical candidate: ' + box['text'])
            print('Expected coords: ' + str(expected_coords) + ' Box coords: ' + str(box['coordinates']))
            distance = calculate_distance(expected_coords, (box['coordinates'][0], box['coordinates'][1]))

        if distance < min_distance:
            min_distance = distance
            closest_box = box
    return closest_box

def get_spatial_relationship(label_coords, value_coords):
    """
    Determine the spatial relationship (dx, dy) between label and value based on their coordinates.
    """
    dx = value_coords[0] - label_coords[0]
    dy = value_coords[1] - label_coords[1]
    return dx, dy

def apply_spatial_relationship(label_coords, dx, dy):
    """
    Apply the spatial relationship to label coordinates to estimate value coordinates.
    """
    return label_coords[0] + dx, label_coords[1] + dy
