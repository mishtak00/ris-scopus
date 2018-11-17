import csv


class Faculty:

    last_name = ""
    first_name = ""
    id = ""
    affil = ""

    def __init__(self, last: str, first: str, id: str, affil: str):
        self.last_name = last
        self.first_name = first
        self.id = id
        self.affil = affil


def file_compare():
    # the following has 4 return cases
    # 0 for no match at all
    # 1 for last name match
    # 2 for last and first name match
    # 3 for full name and id match
    # 4 for all fields match
    def isEqual(faculty1: Faculty, faculty2: Faculty):
        if (((faculty1.first_name in faculty2.first_name) or (faculty2.first_name in faculty1.first_name))
            and ((faculty1.last_name == faculty2.last_name) or (faculty2.last_name == faculty1.last_name))
            and faculty1.id == faculty2.id
                and ("University of Rochester" in faculty1.affil
                     or "Strong" in faculty1.affil
                     or "Golisano" in faculty1.affil)):
            return 4
        elif (((faculty1.first_name in faculty2.first_name) or (faculty2.first_name in faculty1.first_name))
              and ((faculty1.last_name == faculty2.last_name) or (faculty2.last_name == faculty1.last_name))
              and faculty1.id == faculty2.id):
            return 3
        elif (((faculty1.first_name in faculty2.first_name) or (faculty2.first_name in faculty1.first_name))
              and ((faculty1.last_name == faculty2.last_name) or (faculty2.last_name == faculty1.last_name))):
            return 2
        elif ((faculty1.last_name == faculty2.last_name) or (faculty2.last_name == faculty1.last_name)):
            return 1
        else:
            return 0

    # the following creates a list of the authors affiliated with U of R
    affiliated_list = []

    with open('scopusAuthorsAffiliatedWithUofR.csv', mode='r') as affil_auth:

        line = 0
        reader = csv.reader(affil_auth, delimiter=',')

        for row in reader:
            if (line == 0):
                line += 1
                continue
            elif(row[0]):
                last_first = row[0].split(',')
                # print(last_first[0], last_first[1][1:])
                # the sliced first name is just to delete the leading space char
                try:
                    author = Faculty(last_first[0], last_first[1][1:], row[1], 'University of Rochester')
                # there are a few cases without a first name
                except:
                    # print("no first name for %s" % last_first[0])
                    author = Faculty(last_first[0], '', row[1], 'University of Rochester')

                affiliated_list.append(author)
                # print("Processed %d lines from scopusAuthorsAffiliatedWithUofR.csv" % line)
                line += 1

        print("Processed %d lines from scopusAuthorsAffiliatedWithUofR.csv" % line)
        affil_auth.close()

    # the following populates the comparison code file
    with open('affil_file.csv', mode='r', encoding='latin-1') as current_fac:

        line = 0
        reader = csv.reader(current_fac, delimiter=',')

        comparison_file = open('comparison_file.csv', mode='w', newline='')
        writer = csv.writer(comparison_file, delimiter=',')
        header_names = ['Last Name', 'First Name', 'Scopus ID', 'Current Affiliation', 'Comparison Code']

        for row in reader:
            print("Currently in line %d" % line)
            if (line == 0):
                writer.writerow(header_names)
                line += 1
                continue
            elif(row[0]):
                correct_row = ['', '', '', '', '', '']
                fac = Faculty(row[0], row[1], row[2], row[3])
                comparison_code = -1

                # now time to compare
                for author in affiliated_list:
                    current_comparison_code = isEqual(fac, author)

                    # comparison level is in hierarchy, therefore I am basing the search on the scale from 0 to 3
                    # note that every assignment upon succesful comparison codes (1,2,3) come from the Scopus file
                    if (current_comparison_code > comparison_code):
                        comparison_code = current_comparison_code

                        # if no match at all
                        if (current_comparison_code == 0):
                            # set full name to what's provided by faculty list
                            correct_row[0] = fac.last_name
                            correct_row[1] = fac.first_name
                            correct_row[2] = fac.id
                            correct_row[3] = fac.affil
                            correct_row[4] = '0'

                            # REQUERY THESE ONES ONLY BY FIRST LAST NAME => DONE
                            # faculty might not exist on Scopus
                            if (row[2] == 'DNE'):
                                correct_row[2] = 'DNE'
                                if (row[3] == 'DNE'):
                                    correct_row[3] = 'DNE'

                            # both surname and first name are wrong/written differently
                            elif (fac.id == author.id):
                                correct_row[3] = author.affil
                                correct_row[4] = '5'

                            # if different id because of a weird version of name, prepare for convergence
                            elif ('University of Rochester' in fac.affil
                                    or 'Golisano' in fac.affil
                                    or 'Strong' in fac.affil):
                                correct_row[5] = author.id

                        # code 1 stands for match on last name
                        # this could be two things:
                        # either the first name as shown on the prelim file is wrong/different from Scopus
                        # or the actual faculty member DNE on Scopus
                        elif (current_comparison_code == 1):

                            correct_row[0] = fac.last_name
                            correct_row[1] = fac.first_name
                            correct_row[2] = fac.id
                            correct_row[3] = fac.affil
                            correct_row[4] = '1'

                            # first name is wrong/written differently
                            if (fac.id == author.id):
                                correct_row[3] = author.affil
                                correct_row[4] = '5'

                            # if u of r in affil then must be a new id or sth, check it in cleanup
                            elif ('University of Rochester' in fac.affil
                                    or 'Golisano' in fac.affil
                                    or 'Strong' in fac.affil):
                                correct_row[5] = author.id

                        # code 2 stands for full name match
                        # if only a name match, author exists on scopus
                        # but has different ID than the one returned by initial query
                        elif (current_comparison_code == 2):

                            correct_row[0] = fac.last_name
                            correct_row[1] = fac.first_name
                            correct_row[2] = author.id
                            correct_row[4] = '2'

                            # faculty might not have an affiliation on Scopus
                            # in this case enter id as displayed on Scopus and also CNE
                            # the name match has been coincidental
                            if (fac.affil == 'CNE'):
                                correct_row[3] = 'CNE'

                            elif (fac.affil == 'DNE'):
                                correct_row[3] = 'DNE'
                                correct_row[5] = author.last_name + ',' + author.first_name

                            # if author exists and ids don't match
                            # then enter correct id with code 2
                            # code 2 will signify existence but id correction because
                            # faculty name affiliated with rochester was further down the
                            # search list initially returned by the auth_search query
                            else:
                                correct_row[3] = fac.affil

                        # code 3 signifies a name and id match, but no affiliation match
                        # this takes care of the outdated affiliation problem
                        # basically, code 3 stands for
                        # 'affiliation with U of R is not the current for this author, but is in the list of affiliations'
                        elif (current_comparison_code == 3):

                            correct_row[0] = fac.last_name
                            correct_row[1] = fac.first_name
                            correct_row[2] = author.id
                            correct_row[3] = fac.affil
                            correct_row[4] = '3'

                        # total match, everything's good
                        elif (current_comparison_code == 4):

                            correct_row[0] = fac.last_name
                            correct_row[1] = fac.first_name
                            correct_row[2] = author.id
                            correct_row[3] = fac.affil
                            correct_row[4] = '4'

                writer.writerow(correct_row)
                line += 1

            # if (line == 500):
            #     break
        print("Written %d lines in comparison_file" % line)
        comparison_file.close()
        current_fac.close()
