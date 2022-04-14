from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from sqlite.sqlite import sqlite
from logger.logger import Logger
import os

class Scrapping:
    __log_obj = Logger("logs\\log.log")

    def __init__(self, driver_path):
        chrome_options= webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        self.driver.maximize_window()

    def __get_categories(self):
        try:
            """function that gets all the course categories """
            url = "https://ineuron.ai/"  # base url
            self.driver.get(url)  # opens this url
            self.driver.implicitly_wait(5)  # add wait, so that annoying pop up can be tackled
            x = self.driver.find_elements_by_tag_name("i")  # find the close button
            x[1].click()  # click the close button
            self.driver.implicitly_wait(3)  # add another implicit wait
            course_btn = self.driver.find_element_by_id("course-dropdown")  # get the dropdown button
            course_btn.click()  # click the dropdown button to load the categories
            course_btn.click()  # click the dropdown button to load the categories

            categories = self.driver.find_elements_by_xpath(
                '//li[@id = "course-dropdown"]//a')  # get all the categories

            categories_list = []

            for i in categories:
                categories_list.append(i.text)  # add the categories in categories_list

            Scrapping.__log_obj.add_log("scrapping function executed successfully")

            return categories_list
        except Exception as e:
            Scrapping.__log_obj.add_log("problem in get categories function")
            Scrapping.__log_obj.add_log(str(e))

    def __extract_each_course_url(self, categories_list):
        try:
            """function that finds the urls of all the courses"""
            category_course_dict = {}

            each_category_url = "https://courses.ineuron.ai/category/{}"  # url with which we can iterate over all the categories

            for category in categories_list:  # iterate over all the categories
                try:
                    self.driver.get(each_category_url.format(category))  # get to this category
                    time.sleep(3)
                    # infinite scroll to load all the courses for this category
                    current_height = self.driver.execute_script("return document.body.scrollHeight")  # get the
                    # current height
                    while True:
                        self.driver.execute_script('window.scrollTo(0,arguments[0]);', current_height)
                        time.sleep(3)
                        new_height = self.driver.execute_script("return document.body.scrollHeight")

                        if new_height == current_height:
                            break
                        else:
                            current_height = new_height

                    courses = self.driver.find_elements_by_xpath(
                        '//div[@class="Course_course-card__1_V8S Course_card__2uWBu card"]//a')  # load all the courses

                    # create the dictionary where keys are categories and values are urls
                    for course in courses:
                        if category in category_course_dict:
                            category_course_dict[category].append(course.get_attribute("href"))
                        else:
                            category_course_dict[category] = [course.get_attribute("href")]


                except Exception as e:  # if there is a problem in this category, skip it.
                    continue

            Scrapping.__log_obj.add_log("scrapping function successful")
            return category_course_dict
        except Exception as e:
            Scrapping.__log_obj.add_log("problem in Scrapping function")
            Scrapping.__log_obj.add_log(str(e))

    def __extract_data(self, category_course_dict, database, table, limit):
        try:
            """extracts the data and dumps the data into the given table of the given database"""

            max_courses_per_category = limit  # max course to be extracted per category

            sqlite_obj = sqlite(database)  # create sqlite object

            query = 'insert into {} VALUES("{}","{}","{}","{}","{}","{}","{}","{}","{}")'  # generic query to insert
            # values inside a table.

            for category in category_course_dict.keys(): # iterate over all the categories
                total_course = 0  # counter, which ensures we only extract a limited courses per category

                for url in category_course_dict[category]:  # iterate over all the urls of this category
                    try:
                        if total_course < max_courses_per_category:   # check if total_courses don't exceed max_courses_per_category
                            cat = category  # extract category
                            self.driver.get(url)

                            # adding explicit wait to close the annoying pop up
                            wait = WebDriverWait(self.driver, 10)
                            close_btn = wait.until(
                                EC.presence_of_element_located(
                                    (By.XPATH, '//div[@class="Modal_modal-content-md__ogBrj card"]//i')))
                            close_btn.click()

                            # extract course name
                            course_name = self.driver.find_element_by_class_name("Hero_course-title__1a-Hg").text

                            # extract description
                            description = self.driver.find_element_by_class_name("Hero_course-desc__26_LL").text

                            # extract price
                            price = self.driver.find_element_by_class_name("CoursePrice_dis-price__3xw3G").text

                            #  extract time
                            time_list = self.driver.find_elements_by_class_name("CoursePrice_time__1I6dT")


                            try:
                                class_timing = time_list[0].text
                                doubt_timing = time_list[1].text

                            except:
                                class_timing = ""
                                doubt_timing = ""

                            # extract mentors
                            mentors_list = self.driver.find_elements_by_xpath(
                                '//div[@class="InstructorDetails_left__3jo8Z"]//h5')

                            mentors = ""

                            for i in mentors_list:
                                mentors += i.text + ","

                            # extract features
                            features_list = self.driver.find_elements_by_xpath(
                                '//div[@class="CoursePrice_course-features__2qcJp"]//li')

                            features = ""

                            for i in features_list:
                                features += i.text + ","

                            # extract syllabus
                            syllabus_list = self.driver.find_elements_by_xpath(
                                '//div[@class="CourseLearning_card__WxYAo card"]//li')
                            syllabus = ""

                            for i in syllabus_list:
                                syllabus += i.text + ","


                            # get the current query
                            current_query = query.format(table, cat, course_name, description, price, class_timing,
                                                         doubt_timing, mentors, features, syllabus)

                            # execute the query
                            sqlite_obj.execute_query_with_commit(current_query)

                            total_course += 1 # increment the counter
                        else:  # break the loop if we reach max_courses_per_category
                            break

                    except:
                        continue
            Scrapping.__log_obj.add_log("extract data successful")
        except Exception as e:
            Scrapping.__log_obj.add_log("problem in extracting data from extract function")
            Scrapping.__log_obj.add_log(str(e))

    def scrapping(self, database, table, limit):
        try:
            """main function to perform actual scrapping"""
            categories_list = self.__get_categories()
            categories_course_dict = self.__extract_each_course_url(categories_list)
            self.__extract_data(categories_course_dict, database, table, limit)
            Scrapping.__log_obj.add_log("scrapping function successful")
            return categories_list
        except Exception as e:
            Scrapping.__log_obj.add_log("problem in scrapping function")
            Scrapping.__log_obj.add_log(str(e))
