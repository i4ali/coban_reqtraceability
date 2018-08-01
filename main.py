import requests
import csv
from itertools import chain

PROJECT_ID = '13107'
STORYTYPEISSUE_ID = '10001'
TESTTYPEISSUE_ID = '10600'
USER = 'imrana@cobantech.com'
PASSWORD = 'Fall2016'
maxResults = 50


def id_generator(dict_var):
    for k, v in dict_var.items():
        if k == "id":
            yield v
        elif isinstance(v, dict):
            for id_val in id_generator(v):
                yield id_val


def main():
    stories = []
    testcoveragestatus = []
    fixversions=[]

    # get total number of issues
    r = requests.get(
        f"https://safefleet.atlassian.net/rest/api/2/search?jql=project={PROJECT_ID} AND issuetype={STORYTYPEISSUE_ID}",
        auth=(USER, PASSWORD))
    total = r.json()['total']

    # call endpoint until all results are retrieved and stored, this is to obtain
    # issue keys(e.g HS-317) for all the issues in the project. The while loop deals with pagination that happens
    # after maxResults
    startat = 0
    while (total-startat) > 0:
        r = requests.get(f"https://safefleet.atlassian.net/rest/api/2/search?jql=project={PROJECT_ID} AND issuetype={STORYTYPEISSUE_ID}&startAt={startat}",
                         auth=(USER, PASSWORD))
        rawdata_project_stories = r.json()

        project_stories = rawdata_project_stories['issues']

        for project_story in project_stories:
            stories.append(project_story['key'])

        startat += maxResults

    # obtain fix versions for all issues retrieved above
    for story in stories:
        r2 = requests.get(f"https://safefleet.atlassian.net/rest/api/2/issue/{story}?fields=fixVersions",
                          auth=(USER, PASSWORD))
        rawdata_fixversion = r2.json()
        if not rawdata_fixversion['fields']['fixVersions']:
            fixversions.append('None')
        else:
            for d in rawdata_fixversion['fields']['fixVersions']:
                if 'name' in d:
                    fixversions.append(d['name'])

    # call endpoint for all the issues captured above to determine linked issues of type test
    for story in stories:
        r3 = requests.get(f"https://safefleet.atlassian.net/rest/api/2/issue/{story}?fields=issuelinks",
                        auth=(USER, PASSWORD))

        rawdata_story = r3.json()

        story_links = rawdata_story['fields']['issuelinks']

        # determine if there is a linked issue for the main issue, this is to obtain
        # status of test linked to stories
        coveragestatus=False
        for story_link in story_links:
            for x in id_generator(story_link):
                if x == TESTTYPEISSUE_ID:
                    coveragestatus=True
        testcoveragestatus.append(coveragestatus)

    # combine all the lists collected into one
    result = dict(zip(stories, zip(fixversions, testcoveragestatus)))

    # write the output to file
    with open('requirement_test_coverage.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Story', 'FixVersion', 'TestCoverage'])
        for key, value in result.items():
            writer.writerow([key, value[0], value[1]])


if __name__ == '__main__':
    main()
