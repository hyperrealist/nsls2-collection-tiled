import argparse
import os
import json


def main():
    parser = argparse.ArgumentParser(description='Generate a report of status of each beamline for a python version')
    parser.add_argument("-p", "--python_version", help="The python ver for Conda")
    parser.add_argument("-a", "--action_run", help="The ID(s) of current workflow")
    parser.add_argument("-j", "--json_name", default="workflow_info",
                        help="jsonfile containing info about previous job of current workflow")
    parser.add_argument("-m", "--markdown_name", default="job_info",
                        help="markdown file containing info about previous job of current workflow")
    parser.add_argument("-o", "--org", default="StaticYolt",
                        help="organization of the repo to call GH api")
    parser.add_argument("-r", "--repo", default="nsls2-collection-tiled",
                        help="repository to find actions from")
    args = parser.parse_args()
    os.system(f'''gh api \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        /repos/{args.org}/{args.repo}/actions/runs/{args.action_run}/jobs > {args.json_name}.json''')

    chosen_python_version = str(args.python_version)
    relevant_jobs = []
    success_jobs = []
    failure_jobs = []
    cancelled_jobs = []

    f = open(f'{args.json_name}.json')
    data = json.load(f)

    def sort_by_py_version(data):
        for element in data['jobs']:
            if element['name'][-4:] == chosen_python_version:
                print(element)
                relevant_jobs.append(element)

    sort_by_py_version(data)
    for element in relevant_jobs:
        conclusion = element['conclusion']
        match conclusion:
            case "success":
                success_jobs.append(element)
            case "failure":
                failure_jobs.append(element)
            case "cancelled":
                cancelled_jobs.append(element)
            case _:
                # This should never happen
                print("ERROR")

    num_total_tests = len(relevant_jobs)
    num_success_jobs = len(success_jobs)
    success_percentage = int(float(num_success_jobs / num_total_tests) * 100)

    md = open(f"{args.markdown_name}.md", "w")
    md.write("### Success Rate: " + str(success_percentage) + "%\n")
    md.write("|Beamline|Conclusion|\n")
    md.write("|:---:|:---:|\n")

    # looping like this to give more control over sorting in the future
    for element in relevant_jobs:
        element_name = element['name'].split(" ")[3].split("-")[0]
        if element in success_jobs:
            success_msg = "success"
            md.write(f"|{element_name}|{success_msg}|")
        elif element in failure_jobs:
            failure_msg = "failure"
            md.write(f"|{element_name}|{failure_msg}|")
        elif element in cancelled_jobs:
            cancelled_msg = "cancelled"
            md.write(f"|{element_name}|{cancelled_msg}|")
        else:
            print("ERROR")
        md.write("\n")

    md.close()
    f.close()


if __name__ == "__main__":
    main()