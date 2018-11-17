import csv
from search import *


def query():

    with open('update.csv', mode='r') as final:

        reader = csv.reader(final, delimiter=',')
        line = 0

        queried = open('update_queried.csv', mode='w', newline='')
        queried_writer = csv.writer(queried, delimiter=',')

        for row in reader:

            print("Currently in line %d" % line)

            if (line == 0):
                queried_writer.writerow(row)
                line += 1
                continue

            else:

                if (row[4] == 'UPDATE'):

                    auth_data = detailed_auth_query(row[0], row[1])

                    # if UR was found somewhere in the lists of authors and their histories
                    if (auth_data[3] != 'max' and auth_data[3] != 'na' and auth_data[3] != 'DNE'):

                        # if the ID is the same as the original one as read
                        # then UR was down the list of affil history
                        if (row[2] == auth_data[2]):
                            auth_data.append('UPDATE, 1st')

                        # if the ID is different from the one read
                        # then author was a different person
                        else:
                            auth_data.append('UPDATE, further down')

                        #auth_data += [row[5], row[6]]

                    # if UR isn't found at all, means either one of two things
                    else:

                        # if the query hit the results cap of 25
                        if (auth_data[3] == 'max'):
                            auth_data += ['HIT MAX']

                        # if the query didn't find anything
                        elif (auth_data[3] == 'na' or auth_data[3] == ''):
                            auth_data += ['UNKNOWN']

                        elif (auth_data[3] == 'DNE'):
                            auth_data += ['DNE']

                        auth_data[2] = ''
                        auth_data[3] = ''
                        #auth_data += [row[5], row[6]]

                    queried_writer.writerow(auth_data)

                else:
                    queried_writer.writerow(row)

                line += 1

                # if (line == 30):
                #     break

        queried.close()
        final.close()
