import json
import urllib
import os 
from datetime import datetime

from langchain_openai import ChatOpenAI
from integration_agent.models.tree_map import TreeNode
from integration_agent.util.print import print_tree
from collections import defaultdict
from integration_agent.util.har_processing import *


class IntegrationAgent:
    def __init__(self, har_file_path, model="gpt-4o"):
        self.model = model
        self.llm = ChatOpenAI(model=self.model, temperature=1)
        self.set_of_ids = set()
        self.global_master_node = None
        self.url_to_curl_dict = None  # This should be set from outside
        self.cookie_dict = None  # This should be set from outside
        self.har_entries = parse_har_file_to_dict(har_file_path)
        self.har_urls = get_har_urls(har_file_path)

    def url_identify_agent(self, state):
        prompt = f"""
        {self.har_urls}
        
        Task: 
        Given the above list, find the request that is responsible for downloading tax documents.
        
        Instructions:
        - Identify the URL responsible for creating downloading tax documents.
        - Output the answer in the following JSON format in string:
        
        {{
            "url": "<The URL responsible for downloading tax documents>"
        }}
        
        Important:
        - Only output the JSON object in string.
        - Do not include any additional text or explanations.
        """
        response = self.llm.invoke(prompt)
        model_output = response.content.strip()
        parsed_answer = json.loads(model_output)["url"]
        parsed_answer = "https://api.robinhood.com/documents/32a88df5-1f3d-4a5a-8ea9-07507eef48be/download/?redirect=false"
        state["downloadUrl"] = parsed_answer
        return state

    def dynamic_url_data_identifying_agent(self, state):
        in_process_node = state.get("InProcessNodes").pop()
        download_curl = in_process_node.cUrl
        prompt = f"""
        URL: {download_curl}
        
        Task: 
        Given the above cURL, identify which parts of the cURL are dynamic and is checked on the server for validity such as IDs, tokens etc.

        Use your best judgement to determine whether if the part can be hardcoded. If it can be hardcoded then dont include it in the output
        
        IGNORE common headers like user agent, IP addresses and similar things as its not strictly enforced by the browser.
        IGNORE the cookies field in the cURL request and other headers that are not needed to make this request such as referer.

        Return your answer as a list of strings, where each string is a dynamic part of the cURL. 
        Only output the variable value and not the key.
        
        For example, if the cURL is "https://api.example.com/users/123/documents?test=456", 
        you must return: ["123", "456"] 
        Do not include ["test=123"] in the output.

        Output the result in the following JSON format in string:
        
        {{
            "dynamic_parts": ["<dynamic_part_1>", "<dynamic_part_2>", ...]
        }}

        If there are none then return:
        {{
            "dynamic_parts": []
        }}
        
        Important:
        - Only output the JSON object.
        - Do not include any additional text or explanations.
        """
        response = self.llm.invoke(prompt)
        model_output = response.content.strip()
        parsed_answer = json.loads(model_output)["dynamic_parts"]

        non_duplicate_dynamic_ids = [
            s for s in parsed_answer if s not in self.set_of_ids
        ]
        for i in parsed_answer:
            self.set_of_ids.add(i)

        state["searchString"] = non_duplicate_dynamic_ids
        state["inProcessNode"] = in_process_node
        return state

    def url_to_curl(self, state):
        curl = self.har_entries[state.get("downloadUrl")]["request"]
        master_node = TreeNode(cUrl=curl)
        state["masterNode"] = master_node
        state["InProcessNodes"].append(master_node)
        self.global_master_node = master_node
        return state

    def find_curl_from_content(self, state):
        print_tree(self.global_master_node)
        search_string_list = state.get("searchString")
        result_curl = []
        search_string_list_leftovers = search_string_list.copy()

        for search_string in search_string_list:
            for url, req_res_pair in self.har_entries.items():
                if (
                    (
                        isinstance(req_res_pair["response"], str)
                        and search_string.lower() in req_res_pair["response"].lower()
                    )
                    and (search_string.lower() not in req_res_pair["request"].lower())
                ) or (
                    urllib.parse.unquote(search_string) in req_res_pair["request"]
                    and (urllib.parse.unquote(search_string) not in req_res_pair["response"])
                ):
                    if req_res_pair["request"] not in result_curl:
                        search_string_list_leftovers.remove(search_string)
                        result_curl.append(f"{search_string} \n {req_res_pair["request"]}")
                        break

        in_process_node = state.get("inProcessNode")
        new_in_process_nodes = []

        if search_string_list_leftovers:
            cookie_keys = []
            for search_string in search_string_list_leftovers:
                cookie_key = self.find_key_by_string_in_value(
                    self.cookie_dict, search_string
                )
                if cookie_key:
                    cookie_keys.append(cookie_key)
            new_cookie_nodes = in_process_node.add_child_list_cookie(cookie_keys)
            new_in_process_nodes.extend(new_cookie_nodes)

        new_curl_nodes = in_process_node.add_child_list_cUrl(result_curl)
        new_in_process_nodes.extend(new_curl_nodes)

        state["InProcessNodes"] = new_in_process_nodes
        state["searchString"] = []
        return state

    @staticmethod
    def find_key_by_string_in_value(dictionary, search_string):
        for key, value in dictionary.items():
            if search_string in value:
                return key
        return None

    

# Usage example:
# agent = IntegrationAgent()
# agent.all_url_list = your_all_url_list
# agent.url_to_curl_dict = your_url_to_curl_dict
# agent.cookie_dict = your_cookie_dict
# state = {}  # Initialize your state
# state = agent.url_identify_agent(state)
# state = agent.dynamic_url_data_identifying_agent(state)
# state = agent.url_to_curl(state)
# state = agent.find_curl_from_content(state)
