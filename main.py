import requests
import csv
from itertools import chain

PROJECT_ID = '13107'
STORYTYPEISSUE_ID = '10001'
TESTTYPEISSUE_ID = '10600'
USER = 'imrana@cobantech.com'
PASSWORD = 'Fall2016'
maxResults = 50


class JiraProjectStats:

    STORYTYPEISSUE_ID = '10001'
    TESTTYPEISSUE_ID = '10600'
    
    def __init__(self, user, password, project_id):
        self.user = user
        self.password = password
        self.maxresults = 50
        self.startat = 0
        self.project_id = project_id
        self.issue_stats = []
        self.issue_keys = []
        
    def _get_total_issue_count(self):
        self._get_issues_first_page(STORYTYPEISSUE_ID)
        self.total = self.response_first_page.json()['total']

    def _get_issues_first_page(self, issue_type_id):
        self.response_first_page = requests.get(
            f"https://safefleet.atlassian.net/rest/api/2/search?jql=project={self.project_id} AND \
            issuetype={issue_type_id}&startAt=0",
            auth=(USER, PASSWORD))
         
    def get_all_issue_keys(self):
        self._get_total_issue_count()
        while (self.total - self.startat) > 0:
            issues = self._get_issue_keys_per_page(STORYTYPEISSUE_ID)
            for issue in issues:
                self.issue_keys.append(issue['key'])
            self.startat += self.maxresults
        return self.issue_keys

    def _get_issue_keys_per_page(self, issue_type_id):
        res = requests.get(
            f"https://safefleet.atlassian.net/rest/api/2/search?jql=project={self.project_id} AND issuetype={issue_type_id}&startAt={self.startat}",
            auth=(USER, PASSWORD))
        issues = res.json()['issues']
        return issues

    def get_fix_version_for_issue(self,issue_key):
        res = requests.get(f"https://safefleet.atlassian.net/rest/api/2/issue/{issue_key}?fields=fixVersions",\
                           auth=(USER, PASSWORD))
        res_json = res.json()
        if not res_json['fields']['fixVersions']:
            fixversion = 'None'
        else:
            for d in res_json['fields']['fixVersions']:
                if 'name' in d:
                    fixversion = d['name']
        return fixversion

    def is_test_type_linked(self, issue_key):
        res = requests.get(f"https://safefleet.atlassian.net/rest/api/2/issue/{issue_key}?fields=issuelinks",
                         auth=(USER, PASSWORD))
        res_json = res.json()
        links = res_json['fields']['issuelinks']
        coveragestatus=False
        for link in links:
            for x in self.id_generator(link):
                if x == TESTTYPEISSUE_ID:
                    coveragestatus=True
        return coveragestatus

    def id_generator(self,dict_var):
        for k, v in dict_var.items():
            if k == "id":
                yield v
            elif isinstance(v, dict):
                for id_val in self.id_generator(v):
                    yield id_val



    
j = JiraProjectStats("imrana@cobantech.com", 'Fall2016', '13107')
issue_keys = j.get_all_issue_keys()
d = {}
stats = []

for issue_key in issue_keys:
    d['key'] = issue_key
    d['fixVersion'] = j.get_fix_version_for_issue(issue_key)
    d['testCoverage'] = j.is_test_type_linked(issue_key)
    stats.append(d)
    #d['testCoverage']

print(stats)




# def get_all_issues(PROJECT_ID, STORYTYPEISSUE_ID, USER, PASSWORD, maxResults):
#     """

#     :param PROJECT_ID: PROJECT ID number for the project found in JIRA
#     :param STORYTYPEISSUE_ID: ISSUE ID number of the type of issue found in JIRA
#     :param USER:
#     :param PASSWORD:
#     :param maxResults: pagination default value as per JIRA API
#     :return: a list of all project stories
#     """
#     startat = 0
#     project_stories = []

#     res = requests.get(
#         f"https://safefleet.atlassian.net/rest/api/2/search?jql=project={PROJECT_ID} AND issuetype={STORYTYPEISSUE_ID}",
#         auth=(USER, PASSWORD))
#     total = res.json()['total']  # Total number of issues


#     while (total - startat) > 0:
#         res = requests.get(
#             f"https://safefleet.atlassian.net/rest/api/2/search?jql=project={PROJECT_ID} AND issuetype={STORYTYPEISSUE_ID}&startAt={startat}",
#             auth=(USER, PASSWORD))
#         rawdata_project_stories = res.json()
#         project_stories.append(rawdata_project_stories['issues'])
#         startat += maxResults
#     return project_stories


# def id_generator(dict_var):
#     for k, v in dict_var.items():
#         if k == "id":
#             yield v
#         elif isinstance(v, dict):
#             for id_val in id_generator(v):
#                 yield id_val


# def main():
#     stories = []
#     testcoveragestatus = []
#     fixversions=[]

#     # get total number of issues
#     r = requests.get(
#         f"https://safefleet.atlassian.net/rest/api/2/search?jql=project={PROJECT_ID} AND issuetype={STORYTYPEISSUE_ID}",
#         auth=(USER, PASSWORD))
#     total = r.json()['total']

#     # call endpoint until all results are retrieved and stored, this is to obtain
#     # issue keys(e.g HS-317) for all the issues in the project. The while loop deals with pagination that happens
#     # after maxResults
#     startat = 0
#     while (total-startat) > 0:
#         r = requests.get(f"https://safefleet.atlassian.net/rest/api/2/search?jql=project={PROJECT_ID} AND issuetype={STORYTYPEISSUE_ID}&startAt={startat}",
#                          auth=(USER, PASSWORD))
#         rawdata_project_stories = r.json()

#         project_stories = rawdata_project_stories['issues']

#         for project_story in project_stories:
#             stories.append(project_story['key'])

#         startat += maxResults

#     # obtain fix versions for all issues retrieved above
#     for story in stories:
#         r2 = requests.get(f"https://safefleet.atlassian.net/rest/api/2/issue/{story}?fields=fixVersions",
#                           auth=(USER, PASSWORD))
#         rawdata_fixversion = r2.json()
#         if not rawdata_fixversion['fields']['fixVersions']:
#             fixversions.append('None')
#         else:
#             for d in rawdata_fixversion['fields']['fixVersions']:
#                 if 'name' in d:
#                     fixversions.append(d['name'])

#     # call endpoint for all the issues captured above to determine linked issues of type test
#     for story in stories:
#         r3 = requests.get(f"https://safefleet.atlassian.net/rest/api/2/issue/{story}?fields=issuelinks",
#                         auth=(USER, PASSWORD))

#         rawdata_story = r3.json()

#         story_links = rawdata_story['fields']['issuelinks']

#         # determine if there is a linked issue for the main issue, this is to obtain
#         # status of test linked to stories
#         coveragestatus=False
#         for story_link in story_links:
#             for x in id_generator(story_link):
#                 if x == TESTTYPEISSUE_ID:
#                     coveragestatus=True
#         testcoveragestatus.append(coveragestatus)

#     # combine all the lists collected into one
#     result = dict(zip(stories, zip(fixversions, testcoveragestatus)))

#     # write the output to file
#     with open('requirement_test_coverage.csv', 'w', newline='') as csv_file:
#         writer = csv.writer(csv_file)
#         writer.writerow(['Story', 'FixVersion', 'TestCoverage'])
#         for key, value in result.items():
#             writer.writerow([key, value[0], value[1]])


# if __name__ == '__main__':
#     main()
