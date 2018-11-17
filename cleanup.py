import csv


def cleanup():

    all_depts_in_order = []
    all_empl_ids_in_order = []
    with open('faculty.csv', mode='r', encoding='latin-1') as faculty:
        reader = csv.reader(faculty, delimiter=',')
        line = 0
        for row in reader:
            if (line == 0):
                all_depts_in_order.append('Department')
                all_empl_ids_in_order.append('Employee ID')
                line += 1
                continue
            else:
                all_depts_in_order.append(row[2])
                all_empl_ids_in_order.append(row[0])
                line += 1
        faculty.close()

    with open('comparison_file.csv', mode='r', encoding='latin-1') as comparison_file:

        reader = csv.reader(comparison_file, delimiter=',')

        final = open('final.csv', mode='w', newline='')
        writer = csv.writer(final, delimiter=',')

        dne = open('dne.csv', mode='w', newline='')
        dne_writer = csv.writer(dne, delimiter=',')

        add = open('add.csv', mode='w', newline='')
        add_writer = csv.writer(add, delimiter=',')

        merge = open('merge.csv', mode='w', newline='')
        merge_writer = csv.writer(merge, delimiter=',')

        diffname = open('name.csv', mode='w', newline='')
        diffname_writer = csv.writer(diffname, delimiter=',')

        line = 0

        for row in reader:
            print("Currently in line %d" % line)
            correct_row = row[:len(row) - 1]

            if (line == 0):
                correct_row += ['Current status', '', '']
                # append dept at index 5, emplid at 6
                correct_row[5] = all_depts_in_order[line]
                correct_row[6] = all_empl_ids_in_order[line]

                writer.writerow(correct_row)
                dne_writer.writerow(['Last Name', 'First Name'])
                add_writer.writerow(correct_row[:5])
                merge_writer.writerow(correct_row + ['Merge with ID'])
                diffname_writer.writerow(correct_row + ['Found under Name'])
                line += 1
                continue

            else:
                # append dept at index 5, emplid at 6
                correct_row.append(all_depts_in_order[line])
                correct_row.append(all_empl_ids_in_order[line])
                line += 1

                # if all good
                if (row[4] == '4'):
                    correct_row[4] = 'GOOD'
                    writer.writerow(correct_row)
                    continue

                # if author DNE
                if (row[2] == 'DNE'):
                    correct_row[4] = 'DNE'
                    writer.writerow(correct_row)
                    dne_writer.writerow(row[:2])
                    continue

                # if no affiliations exist
                if (row[3] == 'CNE'):
                    correct_row[4] = 'NO AFFIL->ADD'
                    writer.writerow(correct_row)
                    add_writer.writerow(row[:4])
                    continue

                # author is affiliated with UR because there's a full name AND ID match
                if (row[4] == '3'):

                    if ('University of Rochester' in row[3]
                        or 'Golisano' in row[3]
                            or 'Strong' in row[3]):
                        correct_row[4] = 'GOOD'
                        writer.writerow(correct_row)
                        continue

                    # if author has u of r in list but not primary, needs QUERY
                    else:
                        correct_row[4] = 'QUERY'
                        writer.writerow(correct_row)
                        continue

                # if author is only a name match
                if (row[4] == '2'):

                    # if name AND affil match only, it's because of 2 different IDs
                    if ('University of Rochester' in row[3]
                        or 'Golisano' in row[3]
                            or 'Strong' in row[3]):
                        correct_row[4] = 'MERGE'
                        writer.writerow(correct_row)
                        merge_writer.writerow(row[:4] + [row[5]])
                        continue

                    # the author does not pop up under faculty name,
                    # but does under a different name
                    elif (row[3] == 'DNE'):
                        correct_row[4] = 'DIFFERENT NAME'
                        writer.writerow(correct_row)
                        diffname_writer.writerow(row[:4] + [row[5]])
                        continue

                    # author down the list of initial queried authors
                    # and not currently affiliated with U of R
                    else:
                        # this section is to be replaced by the name-based query code
                        # if UR in affil list then update
                        # otherwise add

                        # this is done in query.py

                        # CHECK THE ONES WITH DNE @ROW[3], THEIR ONLINE NAMES ARE DIFFERENT
                        # PULL THESE OUT UNDER DNE, CHECK NAME => DONE, SEE ABOVE

                        correct_row[4] = 'QUERY'
                        writer.writerow(correct_row)
                        continue


                # if author id match only and either first name or full name was different/wrong
                if (row[4] == '5'):
                    correct_row[4] = 'DIFFERENT NAME'
                    writer.writerow(correct_row)
                    diffname_writer.writerow(row[:4]+[row[5]])
                    continue


                if (row[4] == '1'):
                    # if DNE or CNE I take care of it above

                    # if exists and has U of R in affil, 
                    # could be author is written differently on Scopus
                    # like the case of different ID for Rygg, R.
                    if ('University of Rochester' in row[3]
                        or 'Golisano' in row[3]
                            or 'Strong' in row[3]):
                        correct_row[4] = 'GOOD'
                        writer.writerow(correct_row)
                        continue

                    # if no U of R as current affil, different affil only, still write down
                    else:
                        # query auth affiliation history here
                        correct_row[4] = 'QUERY'
                        writer.writerow(correct_row)
                        continue

                # if no match, nor code DNE, nor code 5
                if (row[4] == '0'):

                    # if UR affiliated, might just not be in the cumulative lists,
                    # or is a very recent addition
                    if ('University of Rochester' in row[3]
                        or 'Golisano' in row[3]
                            or 'Strong' in row[3]):
                        correct_row[4] = 'GOOD'
                        writer.writerow(correct_row)
                        continue

                    # if no UR affil, then faculty has diff affil only
                    else:
                        correct_row[4] = 'QUERY'
                        writer.writerow(correct_row)
                        continue

        print("Processed %d lines from comparison_file.csv" % line)
        final.close()
        dne.close()
        add.close()
        merge.close()
        diffname.close()
        comparison_file.close()
