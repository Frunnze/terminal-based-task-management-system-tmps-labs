"""Code for user interaction."""

from domain.models.logic import DB, VigenereCipher, VigenereCipherAdapter, SecurityAbstraction
from domain.models.UI import LoginUI, ObjectivesPageBuilder, TasksPageBuilder
from domain.models.UI import Header, ObjectivesUIList, ObjectivesUIBasicCommands
from domain.models.UI import HeaderDecorator, TasksUICommandsDecorator
from domain.models.UI import TasksUIList, TasksUIBasicCommands
from domain.factory import UserFactory, ManagerFactory


class AppProxy:
    def __init__(self, app) -> None:
        self.app = app

    def run(self):
        print('\n'*50)
        entered = input("App password: ")
        password = 'app123'
        while entered != password:
            print('\n'*50)
            entered = input("App password: ")
        else:
            self.app.run()


class App:
    """The class of the application."""

    def __init__(self):
        self.login_ui  = LoginUI()
        self.user_factory = UserFactory()

        self.security_implementation = VigenereCipherAdapter(VigenereCipher(None))
        self.security_abstraction = SecurityAbstraction(self.security_implementation)
        self.db = DB(self.security_abstraction)

        self.manager_factory = ManagerFactory()


    def run(self):
        """Runs the application, and interacts with the user."""

        self.user_data = None
        while not self.user_data:
            user_name, password = self.login_ui.login()
            user = self.user_factory.create_user(user_name, password)
            self.user_data = self.db.get_user_data(user)

       
        header_object = HeaderDecorator(Header(self.user_data), password)
        objectives_page_builder = ObjectivesPageBuilder(
            header=header_object, 
            objectives=ObjectivesUIList(self.user_data),
            commands=ObjectivesUIBasicCommands())
        objectives_page_builder.create_header()
        objectives_page_builder.create_body()
        objectives_page_builder.create_footer()
        self.objectives_page = objectives_page_builder.get_page()

        tasks_page_builder = TasksPageBuilder(
            header=header_object,
            tasks=TasksUIList(self.user_data),
            commands=TasksUICommandsDecorator(TasksUIBasicCommands()))
        tasks_page_builder.create_header()
        tasks_page_builder.create_body()
        tasks_page_builder.create_footer()
        self.tasks_page = tasks_page_builder.get_page()


        self.tasks_manager = self.manager_factory.create("tasks", self.user_data)
        self.objectives_manager = self.manager_factory.create("objectives", self.user_data)

        self.objectives_page.display_page(self.user_data)

        opened_tasks_ui = False
        while True:
            command = input('Command: ')
            if not opened_tasks_ui:
                if command == '<':
                    self.user_data = None
                    while not self.user_data:
                        user_name, password = self.login_ui.login()
                        user = self.user_factory.create_user(user_name, password)
                        self.user_data = self.db.get_user_data(user)
                    
                    self.objectives_page.header.password = password
                    self.objectives_page.display_page(self.user_data)
                    self.objectives_manager.user_data = self.user_data
                    self.tasks_manager.user_data = self.user_data
                elif command == '+':
                    objective = input(' '*3 + 'Objective name: ')
                    self.user_data = self.objectives_manager.add(objective)
                    self.db.save_user_data(user, self.user_data)
                    self.objectives_page.display_page(self.user_data)
                elif command == '-':
                    objective_number = input(' '*3 + 'Objective number: ')
                    self.user_data = self.objectives_manager.delete(objective_number)
                    self.db.save_user_data(user, self.user_data)
                    self.objectives_page.display_page(self.user_data)
                elif command == 'o':
                    objective_number = input(' '*3 + 'Objective number: ')
                    self.tasks_page.body.obj_num = objective_number
                    self.tasks_page.display_page(self.user_data)
                    opened_tasks_ui = True
                elif command == 'm':
                    objective_number = input(' '*3 + 'Objective number: ')
                    new_title = input(' '*3 + 'New title: ')
                    self.user_data = self.objectives_manager.modify(new_title, objective_number)
                    self.db.save_user_data(user, self.user_data)
                    self.objectives_page.display_page(self.user_data)
            else:
                if command == '<':
                    self.objectives_page.display_page(self.user_data)
                    opened_tasks_ui = False
                elif command == '+':
                    task_title = input(' '*3 + 'Task name: ')
                    due_date = input(' '*3 + 'Due date: ')
                    self.user_data = self.tasks_manager.add(task_title, due_date, objective_number)
                    self.db.save_user_data(user, self.user_data)
                    self.tasks_page.body.obj_num = objective_number
                    self.tasks_page.display_page(self.user_data)
                elif command == '-':
                    task_number = input(' '*3 + 'Task number: ')
                    self.user_data = self.tasks_manager.delete(task_number, objective_number)
                    self.db.save_user_data(user, self.user_data)
                    self.tasks_page.body.obj_num = objective_number
                    self.tasks_page.display_page(self.user_data)
                elif command == 'm':
                    task_number = input(' '*3 + 'Task number: ')
                    new_title = input(' '*3 + 'New title: ')
                    new_dd = input(' '*3 + 'New due date: ')
                    self.user_data = self.tasks_manager.modify(new_title, new_dd, task_number, objective_number)
                    self.db.save_user_data(user, self.user_data)
                    self.tasks_page.body.obj_num = objective_number
                    self.tasks_page.display_page(self.user_data)
                elif command == 'mn':
                    task_number = input(' '*3 + 'Task number: ')
                    new_title = input(' '*3 + 'New title: ')
                    self.user_data = self.tasks_manager.modify_name(new_title, task_number, objective_number)

                    self.db.save_user_data(user, self.user_data)
                    self.tasks_page.body.obj_num = objective_number
                    self.tasks_page.display_page(self.user_data)
                elif command == 'md':
                    task_number = input(' '*3 + 'Task number: ')
                    new_dd = input(' '*3 + 'New due date: ')
                    self.user_data = self.tasks_manager.modify_date(new_dd, task_number, objective_number)

                    self.db.save_user_data(user, self.user_data)
                    self.tasks_page.body.obj_num = objective_number
                    self.tasks_page.display_page(self.user_data)


my_app = AppProxy(App())
my_app.run()