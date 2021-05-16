import logging
import os

logger = logging.getLogger(__name__)

class NER:
    '''
    Helper for Google's Named Entity Recognition (NER) API
    '''
    def __init__(self
        ):

        logger.info(f"Create NER client")
        

    def txt2jsonl(self,
        input_text : (str, 'text to parse'),
        value_dict,
        list_fields
        ) -> (str, 'jsonl payload suitable for training AutoML NER model'):
   
        """Constructs the jsonl for a given pdf.

        Args:
            pdf_text: Text of the pdf.
            value_dict: a dictionary of fieldname: fieldvalue.
        Returns:
            jsonl file suitable for training AutoML NER model
        """

        input_text = input_text.replace('"', '')
        logger.info(f'{input_text}')
        jsonl = ['''{"annotations": [''']
        for field in value_dict:
            value_to_find = value_dict[field]          
            if isinstance(value_to_find, float) and math.isnan(value_to_find):
                continue
            match_fn = list_fields[field]
            match = match_fn.find_match(input_text, value_to_find)
            if match:
                start_index, match_value = match
                if start_index != -1:
                    end_index = start_index + len(match_value)
                    jsonl.append('''{{"text_extraction": {{"text_segment":{{"end_offset": {}, "start_offset": {}}}}}, "display_name": "{}"}},'''.format(
                        end_index, start_index, field))
            else:
                logger.info(f'did not find {field}:{value_to_find}')

        jsonl[-1] = jsonl[-1].replace('"},', '"}')  # Remove last comma
        jsonl.append(u'''],"text_snippet":{{"content":"{}"}}}}'''.format(input_text.replace('\n', '\\n')))

        jsonl_final = "".join(jsonl)
        return jsonl_final

    def extract_field_from_payload(self, text, payload, field_name, default_value='None'):
        """Parses a payload to extract the value of the given field.

        Args
            text: text analyzed by AutoML NER.
            payload: payload returned by AutoML NER.
            field_name: Name of the field to extract.
            default_value: Value to return if the field can not be found.

        Returns:
            extracted value.

        In case the payload contains several times the given field, we take the occurence
            with the highest score.
        """
        value_found = default_value
        score_found = -1
        for result in payload:
            extracted_field_name = result.display_name
            extracted_value_start = result.text_extraction.text_segment.start_offset
            extracted_value_end = result.text_extraction.text_segment.end_offset
            
            extracted_value = text[extracted_value_start:extracted_value_end]

            score = result.text_extraction.score
            
            if (extracted_field_name == field_name) and (score > score_found):
                score_found = score
                value_found = extracted_value
        return value_found
