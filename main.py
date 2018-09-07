import requests
import csv
from itertools import chain



class JiraProjectStats:
   
    def __init__(self, user, password, project_key, api_link):
        self.user = user
        self.password = password
        self.maxresults = 50
        self.startat = 0
        self.api = api_link
        self.project_key = project_key
        self.project_id = self._get_project_id_from_key()
        self.issue_keys = []
        
    def get_total_issue_count(self, issue_type_id):
        self._get_issues_first_page(issue_type_id)
        self.total = self.response_first_page.json()['total']

    def _get_issues_first_page(self, issue_type_id):
        self.response_first_page = requests.get(
            f"{self.api}/search?jql=project={self.project_id} AND issuetype={issue_type_id}&startAt=0",\
            auth=(self.user, self.password))
         
    def get_all_issue_keys(self, issue_type_name):
        issue_type_id = self._get_issue_id_from_name(issue_type_name)
        self.get_total_issue_count(issue_type_id)
        while (self.total - self.startat) > 0:
            issues = self._get_issue_keys_per_page(issue_type_id)
            for issue in issues:
                self.issue_keys.append(issue['key'])
            self.startat += self.maxresults
        return self.issue_keys

    def _get_issue_keys_per_page(self, issue_type_id):
        res = requests.get(
            f"{self.api}/search?jql=project={self.project_id} AND issuetype={issue_type_id}&startAt={self.startat}",
            auth=(self.user, self.password))
        issues = res.json()['issues']
        return issues

    def get_fix_version_for_issue(self, issue_key):
        res = requests.get(f"{self.api}/issue/{issue_key}?fields=fixVersions",\
                           auth=(self.user, self.password))
        res_json = res.json()
        if not res_json['fields']['fixVersions']:
            fixversion = 'None'
        else:
            for d in res_json['fields']['fixVersions']:
                if 'name' in d:
                    fixversion = d['name']
        return fixversion
    
    def is_issue_type_linked_to_issue(self, issue_key, issue_type_name):
        issue_type_id = self._get_issue_id_from_name(issue_type_name)
        res = requests.get(f"{self.api}/issue/{issue_key}?fields=issuelinks",
                         auth=(self.user, self.password))
        res_json = res.json()
        links = res_json['fields']['issuelinks']
        coveragestatus = False
        for link in links:
            for x in self._id_generator(link):
                if x == issue_type_id:
                    coveragestatus = True
        return coveragestatus

    def _id_generator(self, dict_var):
        for k, v in dict_var.items():
            if k == "id":
                yield v
            elif isinstance(v, dict):
                for id_val in self._id_generator(v):
                    yield id_val

    def _get_project_id_from_key(self):
        res = requests.get(f"{self.api}/project",auth=(self.user, self.password))
        res_json = res.json()
        for entry in res_json:
            if entry.get("key") == self.project_key:
                return entry.get("id")
        raise ValueError("no project id found for the key requested")

    def _get_issue_id_from_name(self, issue_type_name):
        res = requests.get(f"{self.api}/issuetype", auth=(self.user,self.password))
        res_json = res.json()
        for entry in res_json:
            if entry.get("name") == issue_type_name:
                return entry.get("id")
        raise ValueError("issue type name is not correct")

    @staticmethod
    def write_to_csv(filename, list_of_dict,  headers=[]):
        with open(filename, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for dict_var in list_of_dict:
                writer.writerow(dict_var)



if __name__ == '__main__':
       
    j = JiraProjectStats("imrana@cobantech.com", 'Fall2016', 'HS', 'https://safefleet.atlassian.net/rest/api/2')
    issue_keys = j.get_all_issue_keys("Story")

    results = []

    count = 0
    for issue_key in issue_keys:
        if count > 5:
            break
        d = {}
        d['key'] = issue_key
        d['fixVersion'] = j.get_fix_version_for_issue(issue_key)
        d['testCoverage'] = j.is_issue_type_linked_to_issue(issue_key, "Test")
        results.append(d)
        count += 1

    j.write_to_csv('requirement_test_coverage.csv', results, headers=['key', 'fixVersion', 'testCoverage'])


