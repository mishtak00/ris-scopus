from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import json
import csv


# Load configuration
con_file = open("config.json")
config = json.load(con_file)
con_file.close()

# Initialize client
client = ElsClient(config['apikey'])
client.inst_token = config['insttoken']


def auth_id_query(auth_id):

    my_auth = ElsAuthor(uri='https://api.elsevier.com/content/author/author_id/%s' % (auth_id))
    # Read author data, then write to disk
    if my_auth.read(client):
        try:
            return my_auth.data['author-profile']['affiliation-history']['affiliation']
        except KeyError:
            print("Query results for '%s' were not structured correctly." % (auth_id))
            # print(my_auth.data['author-profile'])
    else:
        print ("Read author failed.")


def isUR(affil):
    try:
        if ('University of Rochester' in affil
            or 'Golisano' in affil
                or 'Strong' in affil):
            return True
    except TypeError:
        print ("Affiliation was a None type.")


def detailed_auth_query(auth_last, auth_first):

    auth_data = [auth_last, auth_first, '', '']
    print("Searching for author %s, %s" % (auth_last, auth_first))
    # Initialize search object and execute search under the author index
    query = 'authlast(%s)+AND+authfirst(%s)' % (auth_last, auth_first)

    try:
        auth_srch = ElsSearch(query, 'author')
        auth_srch.execute(client, get_all=False)

    except:
        # Load other configuration with new API Key
        con_file = open("config2.json")
        config = json.load(con_file)
        con_file.close()

        # Initialize new client
        client = ElsClient(config['apikey'])
        client.inst_token = config['insttoken']

        auth_srch = ElsSearch(query, 'author')
        auth_srch.execute(client, get_all=False)

    if (len(auth_srch.results) == 1):
        print("auth_srch has", len(auth_srch.results), "result.")
    else:
        print("auth_srch has", len(auth_srch.results), "results.")

    # checking if no results at all
    error_message = auth_srch.results[0].get('error')

    if (len(auth_srch.results) > 0):

        if (not error_message):

            print("Into the results...")

            # grabs the author_id from the search data
            for i in range(len(auth_srch.results)):

                try:
                    string_author_id = auth_srch.results[i].get('dc:identifier')
                    # this line cuts the author id string from the end of AUTHOR_ID
                    # to the end of the id digits
                    author_id = string_author_id[10:]
                    print("author_id : %s" % author_id)
                    auth_data[2] = author_id

                except AttributeError:
                    print("Could not extract auth_id field for %s, %s" % (auth_last, auth_first))
                    auth_data[2] = "CNE"

                # grabs the curr_affil from the search data
                # appends it to auth_data
                try:
                    dict_curr_affil = auth_srch.results[i].get('affiliation-current')
                    curr_affil = dict_curr_affil.get('affiliation-name')
                    print("curr_affil : %s" % curr_affil)

                except AttributeError:
                    print("Could not extract curr_affil field for %s, %s" % (auth_last, auth_first))
                    auth_data[3] = "CNE"

                try:
                    # if UR not current affil go on and search history
                    if (not isUR(curr_affil)):

                        affil_hist = auth_id_query(auth_data[2])

                        try:
                            if (len(affil_hist) > 1):
                                for institution in affil_hist:
                                    try:
                                        affil_instance = institution['ip-doc']['preferred-name']['$']
                                        # if UR affil is found, return immediately
                                        if (isUR(affil_instance)):
                                            curr_affil = affil_instance
                                            auth_data[3] = curr_affil
                                            return auth_data
                                    except:
                                        print("Affiliation instance data for %s,%s wasn't structured correctly." % (auth_data[0], auth_data[1]))
                                        # print(institution)
                            else:
                                try:
                                    affil_instance = affil_hist['ip-doc']['preferred-name']['$']
                                    try:
                                        # if UR affil is found, return immediately
                                        if (isUR(affil_instance)):
                                            curr_affil = affil_instance
                                            auth_data[3] = curr_affil
                                            return auth_data
                                    except TypeError:
                                        print("isUR error")
                                        print(affil_instance)
                                except:
                                    print("Affiliation instance data for %s,%s wasn't structured correctly." % (auth_data[0], auth_data[1]))
                                    # print(institution)

                        except TypeError:
                            print("Type Error occured for affil_hist of %s,%s" % (auth_data[0], auth_data[1]))
                            print(affil_hist)

                    # but if it is then return immediately
                    else:
                        print("Returned with curr_affil : '%s' for %s,%s" % (curr_affil, auth_data[0], auth_data[1]))
                        auth_data[3] = curr_affil
                        return auth_data

                except:
                    print("Something wrong within the returned profile data of %s,%s" % (auth_data[0], auth_data[1]))

            # this is the case of hitting the cap of 25, too many people down the list
            if (len(auth_srch.results) >= 25):
                print("Results CAP of 25 was hit for the %d results of %s,%s" % (len(auth_srch.results), auth_data[0], auth_data[1]))
                auth_data[3] = 'max'
                return auth_data

            # this covers the case of no UR affils found at all
            elif (len(auth_srch.results) < 25):
                print("EXHAUSTED results list of %d results for %s,%s" % (len(auth_srch.results), auth_data[0], auth_data[1]))
                auth_data[3] = 'na'
                return auth_data

        # this could be a false positive! the author name could be in the name-variant field
        # I redo the query down below in the next function
        else:
            auth_data[2] = 'DNE'
            auth_data[3] = 'DNE'
            print(error_message)

    else:
        print("very bad error @ length of auth_srch.results <= 0")
        auth_data[2] = 'NONE'
        auth_data[3] = 'NONE'

    return auth_data


def search():

    def get_auth_name(auth_name_with_comma):
        auth_name = auth_name_with_comma.split(',')
        return auth_name

    # this function returns a list of author data
    # with last name at index 0, first name at 1
    # author id at 2 and current affiliation at 3
    # or DNE in 2 and 3 if doesnt exist on scopus
    # or CNE in 2 and 3 for 'could not extract'
    # for the particular author

    def auth_query(auth_last, auth_first):

        auth_data = [auth_last, auth_first]
        print("Searching for author %s, %s" % (auth_last, auth_first))
        # Initialize search object and execute search under the author index
        query = 'authlast(%s)+AND+authfirst(%s)' % (auth_last, auth_first)

        try:
            auth_srch = ElsSearch(query, 'author')
            auth_srch.execute(client, get_all=False)

        except:
            # Load other configuration with new API Key
            con_file = open("config2.json")
            config = json.load(con_file)
            con_file.close()

            # Initialize new client
            client = ElsClient(config['apikey'])
            client.inst_token = config['insttoken']

            auth_srch = ElsSearch(query, 'author')
            auth_srch.execute(client, get_all=False)

        if (len(auth_srch.results) == 1):
            print("auth_srch has", len(auth_srch.results), "result.")
        else:
            print("auth_srch has", len(auth_srch.results), "results.")

        # checking if no results at all
        error_message = auth_srch.results[0].get('error')

        if (len(auth_srch.results) > 0):

            if (not error_message):
                # grabs the author_id from the search data
                # this assumes that the wanted author is the first one in results
                # check this out later
                try:
                    string_author_id = auth_srch.results[0].get('dc:identifier')
                    # this line cuts the author id string from the end of AUTHOR_ID
                    # to the end of the id digits
                    author_id = string_author_id[10:]
                    print("author_id : %s" % author_id)
                    auth_data.append(author_id)
                except AttributeError:
                    print("Could not extract auth_id field for %s, %s" % (auth_last, auth_first))
                    auth_data.append("CNE")

                # grabs the curr_affil from the search data
                # appends it to auth_data
                try:
                    dict_curr_affil = auth_srch.results[0].get('affiliation-current')
                    curr_affil = dict_curr_affil.get('affiliation-name')
                    print("curr_affil : %s" % curr_affil)
                    auth_data.append(curr_affil)
                except AttributeError:
                    print("Could not extract curr_affil field for %s, %s" % (auth_last, auth_first))
                    auth_data.append("CNE")

            # this could be a false positive! the author name could be in the name-variant field
            # I redo the query down below in the next function
            else:
                auth_data.append("DNE")
                auth_data.append("DNE")
                print(error_message)

        else:
            print("very bad error @ length of auth_srch.results <= 0")
            auth_data.append("none")
            auth_data.append("none")

        return auth_data

    with open('faculty.csv', mode='r') as csv_file:

        line = 0
        reader = csv.reader(csv_file, delimiter=',')

        affil_file = open('affil_file.csv', mode='w', newline='')
        writer = csv.writer(affil_file, delimiter=',')
        header_names = ['Last Name', 'First Name', 'Scopus ID', 'Current Affiliation']

        for row in reader:

            if (line == 0):
                line += 1
                writer.writerow(header_names)
                print("Processed line %d" % line)

            elif (line > 0 and row[0]):
                line += 1
                # print("author_full_name = %s" % row[5])
                auth_name = get_auth_name(row[5])
                auth_last = auth_name[0]
                if ('-' in auth_last):
                    auth_full_last = auth_last.split('-')
                    auth_last = auth_full_last[0]
                elif (' ' in auth_last):
                    auth_full_last = auth_last.split(' ')
                    auth_last = auth_full_last[0]

                auth_first = auth_name[1]
                if (' ' in auth_first):
                    auth_full_first = auth_first.split(' ')
                    one_first = True
                    for i in range(len(auth_full_first)):
                        if (i > 0 and len(auth_full_first[i]) >= 2):
                            one_first = False
                    if (not one_first):
                        auth_first = auth_full_first[0] + ' ' + auth_full_first[1][0]

                # this sends a search request under the author index with given last and first names
                auth_data = auth_query(auth_last, auth_first)

                # requery here with full name if DNE with shortened mid name
                if (auth_data[2] == 'DNE' and ' ' in auth_name[1]):
                    full_first = auth_name[1].split(' ')
                    if (len(full_first[1]) > 1):
                        auth_data = auth_query(auth_last, auth_name[1])

                # this writes every author on a new row in the open affil_file
                # with original faculty full name
                auth_data[0] = auth_name[0]
                auth_data[1] = auth_name[1]
                writer.writerow(auth_data)

                # print("authlast = %s and authfirst = " % auth_name[0], auth_name[1])
                print("Processed line %d" % line)
                # this is here just for testing purposes
                # if (line == 10):
                #     break
            # else:
            #     print("empty row")
        print("Processed %d lines in total" % line)
        affil_file.close()
        csv_file.close()
