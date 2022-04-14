from flask import Flask, render_template, request
from scrapping.scrapping import Scrapping
from sqlite.sqlite import sqlite
import pickle
import os
from logger.logger import Logger

app = Flask(__name__)  # create Flask object

########################################################################################################################

# different parameters

database = "database\\ineuron_scrapping.sqlite"
table = "scrap"
pickle_dump_base_url = "pickle_dump\\"
log_obj = Logger("logs\\log.log")


########################################################################################################################


@app.route("/", methods=['POST', 'GET'])
def index():
    try:
        """ index function. Loads the index.html """
        message = ""  # this helps in when we flush the db. This message is added to the page.
        log_obj.add_log("index function executed")
        return render_template("index.html", message=message)
    except Exception as e:
        log_obj.add_log("problem in index function")
        log_obj.add_log(str(e))


########################################################################################################################

@app.route("/scrapping", methods=['POST', 'GET'])
def scrapping():
    try:
        """view that implements the actual scrapping"""
        # creating objects of sqlite and scrapping

        # create table if it doesn't exist, if it does, don't do anything

        limit = request.values.get(
            "limit")  # fetching the max number of courses to be extracted per category. Helps in saving time.

        if limit.isdigit():  # making sure limit is a digit.
            limit = int(limit)
        else:
            limit = 1

        sqlite_obj = sqlite(db_path=database)  # creating sqlite object. Helps in executing the queries.

        # creating the table if it doesn't exist. If the table does exist, we don't do anything.
        try:
            query = "create table {}(category varchar, course_name varchar, course_description varchar,price varchar, " \
                    "class_time varchar , doubt_time varchar,mentors varchar, features varchar, syllabus varchar " \
                    ")".format(table)
            sqlite_obj.execute_query_with_commit(query)
        except Exception as e:
            pass

        # driver path and actual scrapping
        driver_path = "driver\\chromedriver.exe"
        scrapping_obj = Scrapping(driver_path)  # creating scrapping object

        categories_list = scrapping_obj.scrapping(database, table, limit)  # get the list of categories

        categories_list = list(set(categories_list))  # making sure, we only have unique categories

        # dumping as pickle. This helps in ensuring that even if, we reload the page, the category list is still saved.
        # This helps in the "fetch_results_without_scrap" view. If we don't do this category list won't be persistant.

        with open(pickle_dump_base_url + "category_list.pickle", "wb") as outfile:
            pickle.dump(categories_list, outfile)

        log_obj.add_log("Scrapping function executed successfully")
        return render_template("scraping_success.html", categories_list=categories_list)
    except Exception as e:
        log_obj.add_log("Problem in scrapping function")
        log_obj.add_log(str(e))
        return "<h1> {} </h1>".format(str(e))


########################################################################################################################

@app.route("/results")
def results():
    try:
        """fetches the extracted results for a given query"""
        sqlite_obj = sqlite(db_path=database)  # create sqlite object to execute queries

        category = request.values.get('selected_category')  # get the category for which we want to see the results

        header_query = "PRAGMA table_info({})".format(table)  # query to get the headers of the table
        header_list = [i[1] for i in list(sqlite_obj.execute_query_without_commit(header_query))]  # headers query

        query = 'select * from {} where category LIKE "{}%"'  # generic select query

        current_query = query.format(table, category)  # getting the current select query

        # only fetch those records whose category match this particular category

        res = list(sqlite_obj.execute_query_without_commit(current_query))  # get the results of the select query
        log_obj.add_log("results function executed successfully")
        return render_template("results.html", res=res, header_list=header_list)

    except Exception as e:
        log_obj.add_log("problems in results function")
        log_obj.add_log(str(e))


########################################################################################################################

@app.route("/results_without_scrapping")
def results_without_scrapping():
    try:
        """view function that fetches the results without doing the initial scrapping"""
        # loading the pickle file
        try:
            with open(pickle_dump_base_url + "category_list.pickle", "rb") as infile:
                categories_list = pickle.load(infile)
        except:
            categories_list = []
        log_obj.add_log("results_without_scrapping executed successfully")

        return render_template("scraping_success.html", categories_list=categories_list)
    except Exception as e:
        log_obj.add_log("Problem in results_without_scrapping function")
        log_obj.add_log(str(e))


########################################################################################################################

@app.route("/flush_db")
def flush_db():
    try:
        """view function that helps in flushing the dataset."""
        message = "Database got flushed. Try to do fresh scrapping!!!"

        # check if category_list.pickle exists , if not it means that database is flushed.
        try:
            os.remove(pickle_dump_base_url + "category_list.pickle")
        except:
            pass

        sqlite_obj = sqlite(database)   # creating sqlite object for executing the queries

        query = "delete from {}".format(table) # query to delete the table
        sqlite_obj.execute_query_with_commit(query)

        log_obj.add_log("flush_db function executed successful")
        return render_template("index.html", message=message)
    except Exception as e:
        log_obj.add_log("Problem in flush_db function")
        log_obj.add_log(str(e))


########################################################################################################################

# error handler route
@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


########################################################################################################################
if __name__ == '__main__':
    app.run(debug=True)
