import json

from ner import ner
from sn import sentiment
from TC import text_classification


class NLPApp:
    def __init__(self):
        self.__Load_Database()
        self.__First_Menu()

    # Load Database
    def __Load_Database(self):
        try:
            with open("Database.json", "r") as file:
                self.__Database = json.load(file)
        except FileNotFoundError:
            self.__Database = {}

    # Save Database
    def __Save_Database(self):
        with open("Database.json", "w") as file:
            json.dump(self.__Database, file, indent=4)

    # First Menu
    def __First_Menu(self):
        print("=" * 30)
        print("Hi, How would you like to Proceed")
        print("1. Not a Member ? --Register--")
        print("2. Already a Member ? --Login--")
        print("Anything else to Exit")
        print("=" * 30)

        try:
            user_input = int(input("Enter your Choice - "))
        except ValueError:
            print("Invalid Input")
            self.__First_Menu()
            return

        if user_input == 1:
            self.__Register()
        elif user_input == 2:
            self.__Login()
        else:
            print("Thank You!")
            exit()

    # Register
    def __Register(self):

        print("\n_____ Welcome _____")
        print("=" * 30)

        user_name = input("Enter Full Name - ")
        user_email = input("Enter Email - ")
        user_phone = input("Enter Phone No - ")
        user_password = input("Enter Password - ")

        print("=" * 30)

        if user_email in self.__Database:
            print("Email Already Exists")
            self.__First_Menu()
        else:

            self.__Database[user_email] = {
                "name": user_name,
                "phone": user_phone,
                "password": user_password
            }

            self.__Save_Database()

            print("Registration Successful")
            self.__Login()

    # Login
    def __Login(self):
        
        print("__Login__")
        print("=" * 30)
        user_email = input("Enter Email - ")
        user_password = input("Enter Password - ")

        print("=" * 30)

        if user_email in self.__Database:

            if user_password == self.__Database[user_email]["password"]:

                print(f"\nWelcome {self.__Database[user_email]['name']}")
                self.__Second_Menu()

            else:
                print("Wrong Password")
                self.__Login()

        else:
            print("Email Not Registered")
            self.__Register()

    # Second Menu
    def __Second_Menu(self):

        print("\n" + "=" * 30)
        print("1. Named Entity Recognition")
        print("2. Sentiment Analysis")
        print("3. Text Classification")
        print("4. Logout")
        print("=" * 30)

        try:
            choice = int(input("Enter your Choice - "))
        except ValueError:
            print("Invalid Input")
            self.__Second_Menu()
            return

        if choice == 1:
            self.__NER()

        elif choice == 2:
            self.__SN()

        elif choice == 3:
            self.__TC()

        elif choice == 4:
            self.__First_Menu()

        else:
            print("Invalid Choice")
            self.__Second_Menu()

    
    def __NER(self):

        paragraph = input("\nEnter Paragraph: ")
        result = ner(paragraph)
        print("\n========== Named Entities ==========\n")


        previous = None
        for entity in result:
            word = entity["word"]
            if word.startswith("##"):
                previous["word"] += word.replace("##", "") # type: ignore
                continue
            if previous:
                entity_type = previous["entity_group"]
                if entity_type == "PER":
                    entity_type = "PERSON"
                elif entity_type == "ORG":
                    entity_type = "ORGANIZATION"
                elif entity_type == "LOC":
                    entity_type = "LOCATION"
                elif entity_type == "MISC":
                    entity_type = "MISCELLANEOUS"

                print(f"Entity : {previous['word']}")
                print(f"Type   : {entity_type}")
                print("-" * 30)

            previous = entity

        if previous:
            entity_type = previous["entity_group"]
            if entity_type == "PER":
                entity_type = "PERSON"

            elif entity_type == "ORG":
                entity_type = "ORGANIZATION"

            elif entity_type == "LOC":
                entity_type = "LOCATION"


            print(f"Entity : {previous['word']}")
            print(f"Type   : {entity_type}")
            print("-" * 30)

        self.__Second_Menu()

    
    def __SN(self):
        paragraph = input("\nEnter Text: ")
        result = sentiment(paragraph)
        print("\n========== Sentiment Analysis ==========\n")

        if isinstance(result, list):

            label = result[0]["label"]
            score = result[0]["score"]

            print(f"Sentiment   : {label}")
            print(f"Confidence  : {round(score * 100, 2)}%")
        else:
            print(result)

        self.__Second_Menu()



    
    def __TC(self):

        paragraph = input("\nEnter Text: ")
        labels = [

            "Sports",
            "Politics",
            "Technology",
            "Business"
        ]
        result = text_classification(paragraph, labels)
        print("\n========== Text Classification ==========\n")
        if "labels" in result:


            print(f"Category    : {result['labels'][0]}")
            print(f"Confidence  : {round(result['scores'][0] * 100, 2)}%")

        else:

            print(result)

        self.__Second_Menu()

if __name__ == "__main__":
    obj = NLPApp()
