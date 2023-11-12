import sys, subprocess
from connDB import connection
from PyQt6.QtWidgets import QApplication, QDialog, QStackedWidget, QFileDialog, QMessageBox
from PyQt6.uic import loadUi
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

# Integer expression pattern
pattern_int = QRegularExpression("^[0-9_]+$")

# Create a validator from the pattern
validator_int = QRegularExpressionValidator(pattern_int)

# Float expression pattern
pattern_float = QRegularExpression("^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")

# Create a validator from the pattern
validator_float = QRegularExpressionValidator(pattern_float)


class Data:
    user_name = None
    user_id = 142
    user_type = None


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("LogInPage.ui", self)
        self.LogInButton.clicked.connect(self.go_to_dashboard)

    def go_to_dashboard(self):
        # Retrieve username and password from input fields
        username = self.UserNameLine.text()
        password = self.PasswordLine.text()

        # Validate input fields
        if len(username) == 0 or len(password) == 0:
            QMessageBox.warning(self, "Access denied", "Please input all fields.")
            return

        # Execute SQL query based on user type (admin or user)
        cursor = connection.cursor()
        query, user_type = "", ""

        if self.isAdmin.isChecked():
            query = "SELECT * FROM ADMIN_LOG WHERE ADMIN_USERNAME = %s AND ADMIN_PASSWORD = %s AND ADMIN_STATUS = 'Active'"
            user_type = "admin"
            Data.user_type = "Administrator"
        else:
            query = "SELECT * FROM USER_LOG WHERE USER_USERNAME = %s AND USER_PASSWORD = %s AND USER_STATUS = 'Active'"
            user_type = "user"
            Data.user_type = "User"

        cursor.execute(query, (username, password))
        results = cursor.fetchone()

        # Check if the account exist
        if not results:
            QMessageBox.warning(self, "Access denied", "Account not exist.")
            self.UserNameLine.text()
            return

        # Update global variables
        Data.user_name = results[1]
        Data.user_id = results[0]

        # Get the corresponding dashboard window based on user type
        if user_type == "admin":
            dashboard_window = AdminDashboardWindow()
        else:
            dashboard_window = UserDashboardWindow()

        # Add the dashboard window to the widget stack and set it as current widget
        widget_stack.addWidget(dashboard_window)
        widget_stack.setCurrentWidget(dashboard_window)


class AdminDashboardWindow(QDialog):
    def __init__(self):
        super(AdminDashboardWindow, self).__init__()
        loadUi("AdminDashboard.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.Admin_EmployeeListButton.clicked.connect(self.go_to_employees)
        self.Admin_InventoryButton.clicked.connect(self.go_to_inventory_materials)
        self.Admin_ProjectsButton.clicked.connect(self.go_to_projects)
        self.Admin_AccountsButton.clicked.connect(self.go_to_admin_accounts)
        self.Admin_BackupAndRecover.clicked.connect(self.go_to_admin_backupandrecover)
        self.LogOut.clicked.connect(self.go_to_login)
        self.button_refresh_project.clicked.connect(self.load_reports)
        self.button_showreport.clicked.connect(self.show_report)
        self.load_reports()
        self.insert_projs()


    def show_report(self):
        try:
            project = self.projects_report.currentText()
            cur = connection.cursor()
            cur.execute("SELECT PROJ_NAME, PTLN_START, PTLN_END, PTLN_ACTIVITY FROM PROJECT_TIMELINE "
                        "LEFT JOIN REPORT USING(PTLN_ID) "
                        "LEFT JOIN PROJECT USING(PROJ_ID) "
                        "WHERE PROJ_NAME = %s "
                        "ORDER BY PTLN_ID DESC", (project,))
            reports = cur.fetchall()
            self.tablewidget_proj_report.setRowCount(len(reports))

            for row_index, row_data in enumerate(reports):
                for column_index, column_data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(column_data))
                    self.tablewidget_proj_report.setItem(row_index, column_index, item)

            cur.execute("SELECT PROJ_NAME, INVTR_ETA, INVTR_ACTIVITY FROM INVENTORY_REPORT "
                        "LEFT JOIN REPORT USING(INVTR_ID) "
                        "LEFT JOIN PROJECT USING(PROJ_ID) "
                        "WHERE PROJ_NAME = %s "
                        "ORDER BY INVTR_ID DESC", (project,))
            reports_inv = cur.fetchall()
            self.tablewidget_inventory_report.setRowCount(len(reports_inv))

            for row_index, row_data in enumerate(reports_inv):
                for column_index, column_data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(column_data))
                    self.tablewidget_inventory_report.setItem(row_index, column_index, item)
            cur.close()
        except Exception:
            QMessageBox.information(self, "No Project Selected", "Selece a project to show.")
            return
    def load_reports(self):
        cur = connection.cursor()
        cur.execute("SELECT PROJ_NAME, PTLN_START, PTLN_END, PTLN_ACTIVITY FROM PROJECT_TIMELINE "
                    "LEFT JOIN REPORT USING(PTLN_ID) "
                    "LEFT JOIN PROJECT USING(PROJ_ID) "
                    "ORDER BY PTLN_ID DESC")
        reports = cur.fetchall()
        self.tablewidget_proj_report.setRowCount(len(reports))

        for row_index, row_data in enumerate(reports):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_proj_report.setItem(row_index, column_index, item)

        cur.execute("SELECT PROJ_NAME, INVTR_ETA, INVTR_ACTIVITY FROM INVENTORY_REPORT "
                    "LEFT JOIN REPORT USING(INVTR_ID) "
                    "LEFT JOIN PROJECT USING(PROJ_ID) "
                    "ORDER BY INVTR_ID DESC")
        reports_inv = cur.fetchall()
        self.tablewidget_inventory_report.setRowCount(len(reports_inv))

        for row_index, row_data in enumerate(reports_inv):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_inventory_report.setItem(row_index, column_index, item)
        cur.close()

    def insert_projs(self):
        cur = connection.cursor()
        cur.execute("SELECT PROJ_NAME FROM PROJECT")
        data_proj = cur.fetchall()
        names = [str(row[0]) for row in data_proj]
        self.projects_report.addItems(names)
        cur.close()

    def go_to_employees(self):
        employees = Admin_EmployeeList()
        widget_stack.addWidget(employees)
        widget_stack.setCurrentWidget(employees)

    def go_to_inventory_materials(self):
        inventory_material = Inventory_Material_Admin()
        widget_stack.addWidget(inventory_material)
        widget_stack.setCurrentWidget(inventory_material)

    def go_to_projects(self):
        projects = Admin_Project()
        widget_stack.addWidget(projects)
        widget_stack.setCurrentWidget(projects)

    def go_to_admin_accounts(self):
        admin_acc = AdminAccounts()
        widget_stack.addWidget(admin_acc)
        widget_stack.setCurrentWidget(admin_acc)

    def go_to_admin_backupandrecover(self):
        admin_backupandrecover = Admin_BackupandRecovery()
        widget_stack.addWidget(admin_backupandrecover)
        widget_stack.setCurrentWidget(admin_backupandrecover)

    def go_to_login(self):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            login_window = LoginWindow()
            widget_stack.addWidget(login_window)
            widget_stack.setCurrentWidget(login_window)

class UserDashboardWindow(QDialog):
    def __init__(self):
        super(UserDashboardWindow, self).__init__()
        loadUi("UserDashboard.ui", self)
        self.userNamelbl.setText(Data.user_name)
        self.User_EmployeeListButton.clicked.connect(self.go_to_employees)
        self.User_InventoryButton.clicked.connect(self.go_to_inventory_materials)
        self.User_ProjectsButton.clicked.connect(self.go_to_project)
        self.User_Report_Button.clicked.connect(self.go_to_report)
        self.LogOut.clicked.connect(self.go_to_login)
        self.load_proj_report()
        self.load_inventory_report()

    def load_proj_report(self):
        cur = connection.cursor()
        cur.execute("SELECT PTLN_START, PTLN_END, PTLN_ACTIVITY FROM PROJECT_TIMELINE "
                    "LEFT JOIN REPORT USING(PTLN_ID) "
                    "LEFT JOIN PROJECT USING(PROJ_ID) "
                    "WHERE PROJ_LEADER = %s "
                    "ORDER BY PTLN_ID DESC", (Data.user_id,))
        reports = cur.fetchall()
        self.tablewidget_proj_report.setRowCount(len(reports))

        for row_index, row_data in enumerate(reports):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_proj_report.setItem(row_index, column_index, item)
        cur.close()

    def load_inventory_report(self):
        cur = connection.cursor()
        cur.execute("SELECT INVTR_ETA, INVTR_ACTIVITY FROM INVENTORY_REPORT "
                    "LEFT JOIN REPORT USING(INVTR_ID) "
                    "LEFT JOIN PROJECT USING(PROJ_ID) "
                    "WHERE PROJ_LEADER = %s "
                    "ORDER BY INVTR_ID DESC", (Data.user_id,))
        reports = cur.fetchall()
        self.tablewidget_inventory_report.setRowCount(len(reports))

        for row_index, row_data in enumerate(reports):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_inventory_report.setItem(row_index, column_index, item)
        cur.close()

    def go_to_employees(self):
        employees = User_EmployeeList()
        widget_stack.addWidget(employees)
        widget_stack.setCurrentWidget(employees)

    def go_to_inventory_materials(self):
        inventory_material = Inventory_Material_User()
        widget_stack.addWidget(inventory_material)
        widget_stack.setCurrentWidget(inventory_material)

    def go_to_project(self):
        project_user = Project_User()
        widget_stack.addWidget(project_user)
        widget_stack.setCurrentWidget(project_user)

    def go_to_report(self):
        report = User_Report()
        widget_stack.addWidget(report)
        widget_stack.setCurrentWidget(report)

    def go_to_login(self):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            login_window = LoginWindow()
            widget_stack.addWidget(login_window)
            widget_stack.setCurrentWidget(login_window)


class User_EmployeeList(QDialog):
    def __init__(self):
        super(User_EmployeeList, self).__init__()
        loadUi("EmployeeList_User.ui", self)
        self.Label_user_name.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_user)
        self.button_search.clicked.connect(self.search_emp)
        self.button_load.clicked.connect(self.employee_list)
        self.employee_list()
        self.search_employee.setValidator(validator_int)

    def search_emp(self):
        id = self.search_employee.text()
        cur = connection.cursor()
        cur.execute("SELECT EMP_ID, EMP_FNAME, EMP_MNAME, EMP_LNAME, EMP_ADDRESS, EMP_ZIPCODE, "
                    "EMP_DOB, EMP_AGE, EMP_GENDER, EMP_CIVIL_STATUS, "
                    "EMP_POSITION, EMP_WORK_STATUS, EMP_STATUS, EMP_SSS, EMP_PHILHEALTH, "
                    "EMP_PAGIBIG, PAY_RATE, E.UPDATED_AT, E.CREATED_AT "
                    "FROM EMPLOYEE E "
                    "LEFT JOIN PAYROLL USING(PAY_ID) "
                    "LEFT JOIN PROJECT P USING(PROJ_ID) "
                    "LEFT JOIN USER_LOG U ON P.PROJ_LEADER = U.USER_ID "
                    "WHERE PROJ_ID IS NOT NULL AND U.USER_ID = %s AND EMP_ID = %s", (Data.user_id, id))
        employee_rows = cur.fetchall()

        self.tablewidget_Employee_List.setRowCount(len(employee_rows))

        for row_index, row_data in enumerate(employee_rows):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_Employee_List.setItem(row_index, column_index, item)

        cur.close()

    def employee_list(self):
        cur = connection.cursor()
        cur.execute("SELECT EMP_ID, EMP_FNAME, EMP_MNAME, EMP_LNAME, EMP_ADDRESS, EMP_ZIPCODE, "
                    "EMP_DOB, EMP_AGE, EMP_GENDER, EMP_CIVIL_STATUS, "
                    "EMP_POSITION, EMP_WORK_STATUS, EMP_STATUS, EMP_SSS, EMP_PHILHEALTH, "
                    "EMP_PAGIBIG, PAY_RATE, E.UPDATED_AT, E.CREATED_AT "
                    "FROM EMPLOYEE E "
                    "LEFT JOIN PAYROLL USING(PAY_ID) "
                    "LEFT JOIN PROJECT P USING(PROJ_ID) "
                    "LEFT JOIN USER_LOG U ON P.PROJ_LEADER = U.USER_ID "
                    "WHERE PROJ_ID IS NOT NULL AND U.USER_ID = %s", (Data.user_id,))
        employee_rows = cur.fetchall()

        self.tablewidget_Employee_List.setRowCount(len(employee_rows))

        for row_index, row_data in enumerate(employee_rows):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_Employee_List.setItem(row_index, column_index, item)
        self.search_employee.clear()
        cur.close()

    def back_user(self):
        user_dashboard = UserDashboardWindow()
        widget_stack.addWidget(user_dashboard)
        widget_stack.setCurrentWidget(user_dashboard)


class Inventory_Material_User(QDialog):
    def __init__(self):
        super(Inventory_Material_User, self).__init__()
        loadUi("InventoryListMaterial_user.ui", self)
        self.Label_user_name.setText(Data.user_name)
        self.button_equipment_widget.clicked.connect(self.go_to_inventory_equipment)
        self.backButton.clicked.connect(self.back_user)
        self.assigned_materials()

    def assigned_materials(self):
        cur = connection.cursor()
        cur.execute("SELECT MTL_CODE, INVT_QTY, MTL_NAME, MTL_PRICE, PROJ_NAME, INVT_QTY*MTL_PRICE "
                    "FROM MATERIAL "
                    "LEFT JOIN INVENTORY USING(MTL_CODE) "
                    "LEFT JOIN PROJECT USING(PROJ_ID) "
                    "WHERE PROJ_LEADER = %s", (Data.user_id,))
        materials = cur.fetchall()

        total_cost = sum(item[5] for item in materials)
        total_material = cur.rowcount

        self.label_total_material_cost.setText(f"₱{float(total_cost or 0):,.2f}")
        self.label_total_num_material.setText(str(total_material))

        self.tablewidget_materials_list.setRowCount(len(materials))

        for row_index, row_data in enumerate(materials):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_materials_list.setItem(row_index, column_index, item)
        cur.close()

    def go_to_inventory_equipment(self):
        inventory_equipment = Inventory_Equipment_User()
        widget_stack.addWidget(inventory_equipment)
        widget_stack.setCurrentWidget(inventory_equipment)

    def back_user(self):
        user_dashboard = UserDashboardWindow()
        widget_stack.addWidget(user_dashboard)
        widget_stack.setCurrentWidget(user_dashboard)


class Inventory_Equipment_User(QDialog):
    def __init__(self):
        super(Inventory_Equipment_User, self).__init__()
        loadUi("InventoryListEquipment_user.ui", self)
        self.Label_user_name.setText(Data.user_name)
        self.button_material_button.clicked.connect(self.go_to_inventory_materials)
        self.backButton.clicked.connect(self.back_user)
        self.assigned_equipments()

    def assigned_equipments(self):
        cur = connection.cursor()
        cur.execute("SELECT EQPT_CODE, INVT_QTY, EQPT_NAME, EQPT_PRICE, PROJ_NAME,  INVT_QTY*EQPT_PRICE "
                    "FROM EQUIPMENT "
                    "LEFT JOIN INVENTORY USING(EQPT_CODE) "
                    "LEFT JOIN PROJECT USING(PROJ_ID) "
                    "WHERE PROJ_LEADER = %s", (Data.user_id,))
        equipment = cur.fetchall()

        total_cost = sum(item[5] for item in equipment)
        total_equipment = cur.rowcount

        self.label_total_cost_equipment.setText(f"₱{float(total_cost or 0):,.2f}")
        self.label_total_equipment.setText(str(total_equipment))

        self.tablewidget_equipments_list.setRowCount(len(equipment))

        for row_index, row_data in enumerate(equipment):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_equipments_list.setItem(row_index, column_index, item)
        cur.close()

    def go_to_inventory_materials(self):
        inventory_material = Inventory_Material_User()
        widget_stack.addWidget(inventory_material)
        widget_stack.setCurrentWidget(inventory_material)

    def back_user(self):
        user_dashboard = UserDashboardWindow()
        widget_stack.addWidget(user_dashboard)
        widget_stack.setCurrentWidget(user_dashboard)


class Project_User(QDialog):
    def __init__(self):
        super(Project_User, self).__init__()
        loadUi("User_Project.ui", self)
        self.Label_user_name.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_user)
        self.assigned_project()

    def assigned_project(self):
        cur = connection.cursor()
        cur.execute("SELECT PROJ_ID, PROJ_NAME, USER_NAME, "
                    "PROJ_ADDRESS, PROJ_START, PROJ_END "
                    "FROM PROJECT P "
                    "LEFT JOIN EMPLOYEE USING(PROJ_ID) "
                    "LEFT JOIN INVENTORY USING(PROJ_ID) "
                    "LEFT JOIN USER_LOG U ON P.PROJ_LEADER = U.USER_ID "
                    "WHERE PROJ_STATUS != 'Completed' AND PROJ_LEADER = %s "
                    "GROUP BY PROJ_ID, PROJ_NAME, USER_NAME, PROJ_ADDRESS, PROJ_START, PROJ_END "
                    "LIMIT 1", (Data.user_id,))
        proj_details = cur.fetchone()
        try:

            cur.execute("SELECT count(*) from employee "
                        "join project using(proj_id) "
                        "where proj_leader = %s ",(Data.user_id,))
            emp_nums = cur.fetchone()[0]

            cur.execute("SELECT MTL_CODE FROM PROJECT P "
                        "LEFT JOIN EMPLOYEE USING(PROJ_ID) "
                        "LEFT JOIN INVENTORY USING(PROJ_ID) "
                        "WHERE MTL_CODE IS NOT NULL AND PROJ_LEADER = %s "
                        "GROUP BY MTL_CODE", (Data.user_id,))
            mtl_nums = cur.rowcount

            cur.execute("SELECT EQPT_CODE FROM PROJECT P "
                        "LEFT JOIN EMPLOYEE USING(PROJ_ID) "
                        "LEFT JOIN INVENTORY USING(PROJ_ID) "
                        "WHERE EQPT_CODE IS NOT NULL AND PROJ_LEADER = %s "
                        "GROUP BY EQPT_CODE", (Data.user_id,))
            eqpt_nums = cur.rowcount


            cur.execute("SELECT BDGT_COST FROM BUDGET "
                        "JOIN PROJECT USING(PROJ_ID) "
                        "WHERE PROJ_STATUS != 'Completed' AND PROJ_LEADER = %s "
                        "LIMIT 1", (Data.user_id,))
            cost = cur.fetchone()
            if proj_details and cost:
                self.lbl_proj_id.setText(str(proj_details[0]))
                self.label_project_name.setText(str(proj_details[1]))
                self.label_project_leader.setText(str(proj_details[2]))
                self.label_project_address.setText(str(proj_details[3]))
                self.label_project_start.setText(str(proj_details[4]))
                self.label_project_deadline.setText(str(proj_details[5]))
                self.label_personnels.setText(str(emp_nums))
            if mtl_nums:
                self.label_project_materials.setText(str(mtl_nums))

            if eqpt_nums:
                self.label_project_equipments.setText(str(eqpt_nums))
                self.total_cost.setText("₱{:,.2f}".format(cost[0]))
        except Exception as e:
            print(e)

    def back_user(self):
        user_dashboard = UserDashboardWindow()
        widget_stack.addWidget(user_dashboard)
        widget_stack.setCurrentWidget(user_dashboard)


class User_Report(QDialog):
    def __init__(self):
        super(User_Report, self).__init__()
        loadUi("User_Project_Report.ui", self)
        self.Label_user_name.setText(Data.user_name)
        self.submit_proj_report.clicked.connect(self.proj_report)
        self.submit_inventory_button.clicked.connect(self.inventory_report)
        self.backButton.clicked.connect(self.back_user)

    def proj_report(self):
        activity = self.textEdit_proj.toPlainText()
        start = self.proj_start_date.date().toString(QtCore.Qt.DateFormat.ISODate)
        end = self.proj_end_date.date().toString(QtCore.Qt.DateFormat.ISODate)
        days = self.proj_start_date.date().daysTo(self.proj_end_date.date())
        try:
            if len(activity) == 0:
                QMessageBox.information(self, "Blank Report", "Fill the field.")
                return
            if end < start:
                QMessageBox.information(self, "Invalid Future Date", "Please input valid date.")
                return
            cur = connection.cursor()
            cur.execute("SELECT PROJ_END, PROJ_START FROM PROJECT WHERE PROJ_LEADER = %s AND PROJ_STATUS = 'Ongoing' LIMIT 1",
                        (Data.user_id,))
            proj_dates = cur.fetchone()
            proj_end = proj_dates[0].strftime('%Y-%m-%d')
            proj_start = proj_dates[1].strftime('%Y-%m-%d')

            if (proj_end < end or proj_end < start or proj_start > end or proj_start > start):
                QMessageBox.information(self, "Invalid Date", "Please input valid date.")
                return

            cur.execute("SELECT PTLN_END FROM PROJECT_TIMELINE "
                        "LEFT JOIN REPORT USING(PTLN_ID) "
                        "LEFT JOIN PROJECT USING(PROJ_ID) "
                        " WHERE PROJ_LEADER = %s "
                        "ORDER BY PTLN_END DESC LIMIT 1 ", (Data.user_id))
            latest_report = cur.fetchone()[0].strftime('%Y-%m-%d')
            if latest_report >= end or latest_report >= start:
                QMessageBox.information(self, "Invalid Past Date", "Please input valid date.")
                return

        except Exception as e:
            print(e)

        confirmation = QMessageBox.question(
            self,
            "Submit report",
            "Are you sure you want to submit this report?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:

            cur.execute(
                "INSERT INTO PROJECT_TIMELINE (PTLN_START, PTLN_END, PTLN_DURATION_DAYS, PTLN_ACTIVITY) "
                "VALUES (%s, %s, %s, %s) RETURNING PTLN_ID",
                (start, end, int(days), activity)
            )
            report_id = cur.fetchone()[0]
            connection.commit()
            cur.execute(
                "INSERT INTO REPORT (PROJ_ID, PTLN_ID) "
                "VALUES ((SELECT PROJ_ID FROM PROJECT WHERE PROJ_LEADER = %s AND PROJ_STATUS = 'Ongoing'), %s)",
                (Data.user_id, report_id)
            )
            connection.commit()

            QMessageBox.information(self, "Submitted Report", "Your Project Report is Submitted Successfully.")


    def inventory_report(self):
        inv_act = self.textEdit_inventory.toPlainText()
        eta = self.inventory_arival_date.date().toString(QtCore.Qt.DateFormat.ISODate)
        try:
            if len(inv_act)==0:
                QMessageBox.information(self, "Blank Field", "Fill the field.")
                return
            cur = connection.cursor()
            cur.execute("SELECT PROJ_END, PROJ_START FROM PROJECT WHERE PROJ_LEADER = %s AND PROJ_STATUS = 'Ongoing'",
                        (Data.user_id,))
            proj_dates = cur.fetchone()
            proj_end = proj_dates[0].strftime('%Y-%m-%d')
            proj_start = proj_dates[1].strftime('%Y-%m-%d')
            if proj_start > eta or proj_end < eta:
                QMessageBox.information(self, "Invalid Date", "Please input a valid date.")
                return

            cur.execute("SELECT INVTR_ETA FROM INVENTORY_REPORT "
                        "LEFT JOIN REPORT USING (INVTR_ID) "
                        "LEFT JOIN PROJECT USING (PROJ_ID) "
                        "WHERE PROJ_LEADER = %s "
                        "ORDER BY INVTR_ETA DESC LIMIT 1", (Data.user_id,))
            latest_report = cur.fetchone()[0].strftime('%Y-%m-%d')
            print(latest_report, eta)
            if latest_report >= eta:
                QMessageBox.information(self, "Invalid Past Date", "Please input valid date.")
                return
        except Exception as e:
            print(e)

        confirmation = QMessageBox.question(
            self,
            "Submit report",
            "Are you sure you want to submit this report?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            cur.execute(
                "INSERT INTO INVENTORY_REPORT (INVTR_ETA, INVTR_ACTIVITY) "
                "VALUES (%s, %s) RETURNING INVTR_ID",
                (eta, inv_act)
            )
            report_id = cur.fetchone()[0]
            connection.commit()
            cur.execute(
                "INSERT INTO REPORT (PROJ_ID, INVTR_ID) "
                "VALUES ((SELECT PROJ_ID FROM PROJECT WHERE PROJ_LEADER = %s AND PROJ_STATUS = 'Ongoing'), %s)",
                (Data.user_id, report_id)
            )
            connection.commit()

            QMessageBox.information(self, "Submitted Report", "Your Project Report is Submitted Successfully.")


    def back_user(self):
        user_dashboard = UserDashboardWindow()
        widget_stack.addWidget(user_dashboard)
        widget_stack.setCurrentWidget(user_dashboard)


class Admin_EmployeeList(QDialog):
    def __init__(self):
        super(Admin_EmployeeList, self).__init__()
        loadUi("EmployeeList.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.label_User.setText(Data.user_type)
        if Data.user_type == "Administrator":
            self.backButton.clicked.connect(self.back_admin)
        else:
            self.backButton.clicked.connect(self.back_user)
            self.button_add_employee.setVisible(False)
            self.button_suspend.setVisible(False)
            self.button_unsuspend.setVisible(False)
            self.button_remove.setVisible(False)
            self.button_payroll.setVisible(False)
        self.button_add_employee.clicked.connect(self.go_to_add_employee)
        self.button_payroll.clicked.connect(self.go_to_employee_payroll)
        self.button_load.clicked.connect(self.load_employees)
        self.button_search.clicked.connect(self.search_profile)
        self.button_assigning.clicked.connect(self.go_to_proj_assign)
        self.button_suspend.clicked.connect(self.suspend)
        self.button_unsuspend.clicked.connect(self.unsuspend)
        self.button_remove.clicked.connect(self.remove)
        self.load_employees()

    def suspend(self):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to suspend this employee?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            selected_row = self.tablewidget_Employee_List.currentRow()
            if selected_row != -1:
                employee_ID = self.tablewidget_Employee_List.item(selected_row, 0).text()
                self.tablewidget_Employee_List.removeRow(selected_row)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE EMPLOYEE SET EMP_STATUS = 'Suspend' WHERE EMP_ID = %s AND EMP_STATUS != 'Inactive'",
                        (employee_ID,))
                    connection.commit()
                return

        self.load_employees()

    def unsuspend(self):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to unsuspend this employee?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            selected_row = self.tablewidget_Employee_List.currentRow()
            if selected_row != -1:
                employee_ID = self.tablewidget_Employee_List.item(selected_row, 0).text()
                self.tablewidget_Employee_List.removeRow(selected_row)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE EMPLOYEE SET EMP_STATUS = 'Active' WHERE EMP_ID = %s AND EMP_STATUS != 'Inactive'",
                        (employee_ID,))
                    connection.commit()
                return

        self.load_employees()

    def remove(self):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to remove this employee?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            selected_row = self.tablewidget_Employee_List.currentRow()
            if selected_row != -1:
                employee_ID = self.tablewidget_Employee_List.item(selected_row, 0).text()
                self.tablewidget_Employee_List.removeRow(selected_row)

                with connection.cursor() as cursor:
                    cursor.execute("UPDATE EMPLOYEE SET EMP_STATUS = 'Inactive', PROJ_ID = NULL WHERE EMP_ID = %s",
                                   (employee_ID,))
                    connection.commit()
                return

        self.load_employees()

    def search_profile(self):
        search_emp = self.search_employee.text()
        if not search_emp.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid ID for the search.")
            return
        search_emp = int(search_emp)

        # Employees Accounts table
        cursor = connection.cursor()
        query = "SELECT * FROM EMPLOYEE WHERE EMP_ID = %s"
        cursor.execute(query, (search_emp,))
        employee_row = cursor.fetchone()

        if employee_row is None:
            QMessageBox.warning(self, "Unfound Employee", "Employee not exist!")
            return

        self.tablewidget_Employee_List.setRowCount(1)
        for index, value in enumerate(employee_row):
            self.tablewidget_Employee_List.setItem(0, index, QtWidgets.QTableWidgetItem(str(value)))

        cursor.close()

    def load_employees(self):
        # Employees Accounts table
        self.search_employee.clear()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT EMP_ID, EMP_FNAME, EMP_MNAME, EMP_LNAME, EMP_ADDRESS, EMP_ZIPCODE, EMP_DOB, EMP_AGE, EMP_GENDER, EMP_CIVIL_STATUS, EMP_POSITION, EMP_WORK_STATUS, EMP_STATUS, EMP_SSS, EMP_PHILHEALTH, EMP_PAGIBIG, PAY_RATE, E.UPDATED_AT, E.CREATED_AT "
            "FROM EMPLOYEE E "
            "JOIN PAYROLL USING (PAY_ID) "
            "WHERE EMP_STATUS != 'Inactive' "
            "ORDER BY EMP_ID ASC")
        employee_rows = cursor.fetchall()

        self.tablewidget_Employee_List.setRowCount(len(employee_rows))

        for row_index, row_data in enumerate(employee_rows):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_Employee_List.setItem(row_index, column_index, item)

        cursor.close()

    def go_to_add_employee(self):
        add_employee = Add_Employee()
        widget_stack.addWidget(add_employee)
        widget_stack.setCurrentWidget(add_employee)

    def go_to_employee_payroll(self):
        payroll = Employee_Payroll()
        widget_stack.addWidget(payroll)
        widget_stack.setCurrentWidget(payroll)

    def go_to_proj_assign(self):
        assign_proj = Admin_Assign_Employee_Proj()
        widget_stack.addWidget(assign_proj)
        widget_stack.setCurrentWidget(assign_proj)

    def back_admin(self):
        admin_dashboard = AdminDashboardWindow()
        widget_stack.addWidget(admin_dashboard)
        widget_stack.setCurrentWidget(admin_dashboard)

    def back_user(self):
        user_dashboard = UserDashboardWindow()
        widget_stack.addWidget(user_dashboard)
        widget_stack.setCurrentWidget(user_dashboard)


class Add_Employee(QDialog):
    def __init__(self):
        super(Add_Employee, self).__init__()
        loadUi("EmployeeList_RegistrationForm.ui", self)
        self.Label_user_name.setText(Data.user_name)
        self.label_User.setText(Data.user_type)
        self.backButton.clicked.connect(self.back_employee_list)
        self.button_add_employee.clicked.connect(self.add_employee)
        self.employee_rate.setValidator(validator_float)

        self.required_fields = [
            self.employee_lastname,
            self.employee_firstname,
            self.employee_middlename,
            self.employee_address,
            self.employee_zipcode,
            self.employee_sss,
            self.employee_philhealth,
            self.employee_pagibig,
            self.employee_position,
            self.employee_rate
        ]

    def validate_fields(self):
        for field in self.required_fields:
            if field.text().strip() == "":
                return False
        return True

    def clear_input_values(self):
        for field in self.required_fields:
            field.clear()

    def add_employee(self):
        if self.validate_fields():
            emp_lname = self.employee_lastname.text()
            emp_fname = self.employee_firstname.text()
            emp_mname = self.employee_middlename.text()
            emp_gender = self.employee_gender.currentText()
            emp_dob = self.employee_DOB.date().toString(QtCore.Qt.DateFormat.ISODate)
            current_date = QtCore.QDate.currentDate()
            age = self.employee_DOB.date().daysTo(current_date) // 365
            emp_addrs = self.employee_address.text()
            emp_zip = self.employee_zipcode.text()
            emp_civil_status = self.employee_civil_status.currentText()
            emp_sss = self.employee_sss.text()
            emp_phil = self.employee_philhealth.text()
            emp_pagibig = self.employee_pagibig.text()
            emp_position = self.employee_position.text()
            emp_work_status = self.employee_employment_status.currentText()
            emp_rate = self.employee_rate.text()

            cur = connection.cursor()
            cur.execute("INSERT INTO PAYROLL(PAY_RATE) VALUES(%s) RETURNING PAY_ID", (emp_rate,))
            pay_id = cur.fetchone()[0]
            if Data.user_type == 'Administrator':
                query = "INSERT INTO EMPLOYEE(EMP_LNAME, EMP_FNAME, EMP_MNAME, EMP_GENDER, EMP_AGE, EMP_DOB, EMP_ADDRESS, EMP_ZIPCODE, EMP_CIVIL_STATUS, " \
                        "EMP_SSS, EMP_PHILHEALTH, EMP_PAGIBIG, EMP_POSITION, EMP_WORK_STATUS, PAY_ID, ADMIN_ID) " \
                        "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            else:
                query = "INSERT INTO EMPLOYEE(EMP_LNAME, EMP_FNAME, EMP_MNAME, EMP_GENDER, EMP_AGE, EMP_DOB, EMP_ADDRESS, EMP_ZIPCODE, EMP_CIVIL_STATUS, " \
                        "EMP_SSS, EMP_PHILHEALTH, EMP_PAGIBIG, EMP_POSITION, EMP_WORK_STATUS, PAY_ID, USER_ID) " \
                        "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = (
                emp_lname, emp_fname, emp_mname, emp_gender, age, emp_dob, emp_addrs, emp_zip, emp_civil_status,
                emp_sss,
                emp_phil,
                emp_pagibig, emp_position, emp_work_status, pay_id, Data.user_id)
            cur.execute(query, params)
            connection.commit()
            cur.close()
            # Clear the input values after successful submission
            self.clear_input_values()
            QMessageBox.information(self, "New Employee Added", "Form submitted successfully.")
            self.back_employee_list()
        else:
            QMessageBox.warning(self, "Validation Error", "Please fill in all the required fields.")
            return

    def back_employee_list(self):
        employee_list = Admin_EmployeeList()
        widget_stack.addWidget(employee_list)
        widget_stack.setCurrentWidget(employee_list)


class Employee_Payroll(QDialog):
    def __init__(self):
        super(Employee_Payroll, self).__init__()
        loadUi("Employee_Payroll.ui", self)
        self.Label_user_name.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_employee_list)
        self.button_load.clicked.connect(self.load_payroll)
        self.button_get_salary.clicked.connect(self.get_salary)
        self.button_search.clicked.connect(self.search_employee_salary)
        self.search_employee.setValidator(validator_int)
        self.salary_EmpID.setValidator(validator_int)
        self.pay_dow.setValidator(validator_float)
        self.load_payroll()

    def get_salary(self):
        try:
            emp_ID = self.salary_EmpID.text()
            emp_dow = self.pay_dow.text()
            if len(emp_dow) == 0 or len(emp_ID) == 0:
                QMessageBox.information(self, "Blank Fields", "Please fill all the fields.")
                return

            cur = connection.cursor()
            cur.execute("SELECT * FROM EMPLOYEE WHERE EMP_ID = %s AND EMP_STATUS != 'Inactive'", (emp_ID,))
            exist = cur.fetchall()
            if not exist:
                QMessageBox.information(self, "Not Exist Account", "Please input a valid employee ID")
                return

            confirmation = QMessageBox.question(
                self,
                "Confirmation",
                "Proceed to get the Salary",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                    cur.execute(
                        "UPDATE PAYROLL SET PAY_DOW = %s, PAY_SALARY = PAY_SALARY + (PAY_RATE * %s) "
                        "WHERE PAY_ID = (SELECT PAY_ID FROM PAYROLL JOIN EMPLOYEE USING(PAY_ID) WHERE EMP_ID = %s)",
                        (emp_dow, emp_dow, emp_ID))
                    connection.commit()
                    cur.execute("UPDATE BUDGET SET BDGT_COST = BDGT_COST + (SELECT PAY_SALARY FROM PAYROLL "
                                "JOIN EMPLOYEE USING(PAY_ID) WHERE EMP_ID = %s) "
                                "WHERE PROJ_ID = (SELECT PROJ_ID FROM PROJECT JOIN EMPLOYEE USING(PROJ_ID) "
                                "WHERE EMP_ID = %s)", (emp_ID, emp_ID) )
                    connection.commit()
                    cur.close()
                    self.salary_EmpID.clear()
                    self.pay_dow.clear()
                    self.load_payroll()

        except Exception as e:
            print(e)

    def search_employee_salary(self):
        emp_id = self.search_employee.text()
        if len(emp_id) == 0:
            QMessageBox.information(self, "Blank Field", "Please input valid ID.")
            return

        cur = connection.cursor()
        cur.execute("SELECT * FROM EMPLOYEE WHERE EMP_ID = %s AND EMP_STATUS != 'Inactive'", (emp_id,))
        exist = cur.fetchall()
        if not exist:
            QMessageBox.information(self, "Not Exist Account", "Please input valid employee ID")
            return

        query = '''
                    SELECT EMPLOYEE.EMP_ID, (EMPLOYEE.EMP_FNAME || ' ' || EMPLOYEE.EMP_MNAME || ' ' || EMPLOYEE.EMP_LNAME) AS NAME, PAYROLL.PAY_RATE, PAYROLL.PAY_DOW, PAYROLL.PAY_SALARY, EMPLOYEE.EMP_WORK_STATUS, PROJECT.PROJ_NAME 
                    FROM PAYROLL
                    JOIN EMPLOYEE ON PAYROLL.PAY_ID = EMPLOYEE.PAY_ID
                    JOIN PROJECT ON EMPLOYEE.PROJ_ID = PROJECT.PROJ_ID
                    WHERE EMPLOYEE.EMP_STATUS != 'Inactive' AND EMPLOYEE.EMP_ID = %s
                '''
        cur.execute(query, emp_id)
        employee_rows = cur.fetchall()
        self.tablewidget_Payroll_List.setRowCount(len(employee_rows))

        for row_index, row_data in enumerate(employee_rows):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_Payroll_List.setItem(row_index, column_index, item)

        cur.close()
        self.search_employee.clear()

    def load_payroll(self):
        cur = connection.cursor()
        # SQL query
        query = '''
            SELECT EMPLOYEE.EMP_ID, (EMPLOYEE.EMP_FNAME || ' ' || EMPLOYEE.EMP_MNAME || ' ' || EMPLOYEE.EMP_LNAME) AS NAME, PAYROLL.PAY_RATE, PAYROLL.PAY_DOW, PAYROLL.PAY_SALARY, EMPLOYEE.EMP_WORK_STATUS, PROJECT.PROJ_NAME 
            FROM PAYROLL
            JOIN EMPLOYEE ON PAYROLL.PAY_ID = EMPLOYEE.PAY_ID
            JOIN PROJECT ON EMPLOYEE.PROJ_ID = PROJECT.PROJ_ID
            WHERE EMPLOYEE.EMP_STATUS != 'Inactive'
        '''
        cur.execute(query)
        employee_rows = cur.fetchall()
        self.tablewidget_Payroll_List.setRowCount(len(employee_rows))

        for row_index, row_data in enumerate(employee_rows):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_Payroll_List.setItem(row_index, column_index, item)

        cur.close()

    def back_employee_list(self):
        employee_list = Admin_EmployeeList()
        widget_stack.addWidget(employee_list)
        widget_stack.setCurrentWidget(employee_list)


class Inventory_Material_Admin(QDialog):
    def __init__(self):
        super(Inventory_Material_Admin, self).__init__()
        loadUi("InventoryListMaterial.ui", self)
        self.Label_admin_name.setText(Data.user_name)
        self.button_equipment.clicked.connect(self.go_to_equipment)
        self.button_add_material.clicked.connect(self.add_material)
        self.backButton.clicked.connect(self.back_admin)
        self.button_delete_material.clicked.connect(self.delete_material)
        self.button_update_material.clicked.connect(self.update_quantity)
        self.button_assign_material.clicked.connect(self.assign_material)
        self.update_material_quantity.setValidator(validator_int)
        self.assign_quantity.setValidator(validator_int)
        self.load_materials()
        self.insert_materials()

    def assign_material(self):
        asg_proj = self.assign_proj_ddl.currentText()
        asg_mtl = self.assign_materials_ddl.currentText()
        asg_qty = self.assign_quantity.text()

        if len(asg_qty) == 0:
            QMessageBox.information(self, "Blank field", "Please input a quantity")
            return
        cur = connection.cursor()
        cur.execute(
            "SELECT MTL_CODE FROM INVENTORY WHERE MTL_CODE = (SELECT MTL_CODE FROM MATERIAL WHERE MTL_NAME = %s) AND "
            "PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)", (asg_mtl, asg_proj))
        exist = cur.fetchall()
        if exist:
            QMessageBox.information(self, "Material Exist in Project",
                                    "The material is already assigned to the project.")
            return

        cur.execute(
            "SELECT INVT_QTY FROM INVENTORY WHERE PROJ_ID IS NULL AND MTL_CODE = (SELECT MTL_CODE FROM MATERIAL WHERE MTL_NAME = %s)",
            (asg_mtl,))
        check_qty = cur.fetchone()
        if check_qty[0] < int(asg_qty):
            QMessageBox.information(self, "Invalid Quantity",
                                    "Can't assign quantity. The material quantity is insufficient.")
            return
        try:

            cur.execute(
                "UPDATE INVENTORY SET INVT_QTY = INVT_QTY - %s WHERE PROJ_ID IS NULL AND MTL_CODE = (SELECT MTL_CODE FROM MATERIAL WHERE MTL_NAME = %s)",
                (asg_qty, asg_mtl))
            connection.commit()

            cur.execute("INSERT INTO INVENTORY(INVT_QTY, PROJ_ID, MTL_CODE) "
                        "VALUES(%s, (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s), "
                        "(SELECT MTL_CODE FROM MATERIAL WHERE MTL_NAME = %s))", (asg_qty, asg_proj, asg_mtl))
            connection.commit()
            cur.execute("UPDATE BUDGET SET BDGT_COST = BDGT_COST + (SELECT INVT_QTY*MTL_PRICE FROM MATERIAL "
                        "LEFT JOIN INVENTORY USING(MTL_CODE) "
                        "LEFT JOIN PROJECT USING(PROJ_ID) "
                        "WHERE MTL_NAME = %s AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)) "
                        "WHERE PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)", (asg_mtl, asg_proj, asg_proj))
            connection.commit()
            QMessageBox.information(self, "Assigned Successful", "The material is assigned to the certain project.")
            self.assign_quantity.clear()
            self.load_materials()
            self.insert_materials()
        except Exception as e:
            print(e)

    def update_quantity(self):
        proj_name = self.update_material_projs_ddl.currentText()
        mtl_name = self.update_materials_ddl.currentText()
        mtl_qty = self.update_material_quantity.text()

        if len(mtl_qty) == 0:
            QMessageBox.information(self, "No Quantity", "Enter Material Quantity")
            return

        cur = connection.cursor()
        cur.execute(
            "SELECT INVT_QTY FROM MATERIAL "
            "LEFT JOIN INVENTORY USING (MTL_CODE) "
            "LEFT JOIN PROJECT USING (PROJ_ID) "
            "WHERE PROJ_ID IS NULL AND MTL_NAME = %s", (mtl_name,))

        unassigned_qty = cur.fetchone()

        if proj_name != "Unassigned" and unassigned_qty[0] < int(mtl_qty):
            QMessageBox.information(
                self,
                "Invalid Quantity",
                "Can't subtract quantity. The material quantity is insufficient."
            )
            return

        cur.execute(
            "SELECT PROJ_ID FROM INVENTORY WHERE PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s) "
            "AND MTL_CODE = "
            "(SELECT MTL_CODE FROM MATERIAL WHERE MTL_NAME = %s)", (proj_name, mtl_name))
        proj_assigned = cur.fetchall()
        if proj_name != "Unassigned" and len(proj_assigned) == 0:
            QMessageBox.information(self, "Material not assigned",
                                    "The material is not assigned to the specified project.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Add the material quantity?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            try:

                if proj_name != "Unassigned":

                    cur.execute("UPDATE INVENTORY SET INVT_QTY = INVT_QTY - %s "
                                "WHERE PROJ_ID IS NULL "
                                "AND MTL_CODE = (SELECT MTL_CODE FROM MATERIAL WHERE MTL_NAME = %s)",
                                (mtl_qty, mtl_name))
                    connection.commit()

                    cur.execute("UPDATE INVENTORY SET INVT_QTY = INVT_QTY + %s WHERE MTL_CODE = "
                                "(SELECT MTL_CODE FROM MATERIAL WHERE MTL_NAME = %s) "
                                "AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                                (mtl_qty, mtl_name, proj_name))
                    connection.commit()
                    cur.execute("UPDATE BUDGET SET BDGT_COST = BDGT_COST + (SELECT INVT_QTY*MTL_PRICE FROM MATERIAL "
                                "LEFT JOIN INVENTORY USING(MTL_CODE) "
                                "LEFT JOIN PROJECT USING(PROJ_ID) "
                                "WHERE MTL_NAME = %s AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)) "
                                "WHERE PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                                (mtl_name, proj_name, proj_name))
                    connection.commit()

                else:
                    cur.execute("UPDATE INVENTORY SET INVT_QTY = INVT_QTY + %s WHERE PROJ_ID IS NULL AND MTL_CODE = "
                                "(SELECT MTL_CODE FROM MATERIAL WHERE MTL_NAME = %s)", (mtl_qty, mtl_name))
                    connection.commit()
            except Exception as e:
                print(e)
            self.update_material_quantity.clear()
            self.load_materials()
            self.insert_materials()


    def delete_material(self):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to delete this material?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            try:

                selected_row = self.tablewidget_materials_list.currentRow()
                if selected_row != -1:
                    material_ID = self.tablewidget_materials_list.item(selected_row, 0).text()
                    material_proj = self.tablewidget_materials_list.item(selected_row, 4).text()
                    self.tablewidget_materials_list.removeRow(selected_row)

                    with connection.cursor() as cursor:
                        if material_proj == "Unassigned":
                            cursor.execute("DELETE FROM INVENTORY WHERE MTL_CODE = %s "
                                           "AND PROJ_ID IS NULL",
                                           (material_ID,))
                            cursor.execute("DELETE FROM MATERIAL WHERE MTL_CODE = %s", (material_ID,))

                        else:
                            cursor.execute("SELECT INVT_QTY FROM INVENTORY WHERE MTL_CODE = %s "
                                           "AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                                           (material_ID, material_proj))
                            deleted_material = cursor.fetchone()[0]

                            cursor.execute(
                                "UPDATE BUDGET SET BDGT_COST = BDGT_COST - (SELECT INVT_QTY*MTL_PRICE FROM MATERIAL "
                                "LEFT JOIN INVENTORY USING(MTL_CODE) "
                                "LEFT JOIN PROJECT USING(PROJ_ID) "
                                "WHERE MTL_CODE = %s AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)) "
                                "WHERE PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                                (material_ID, material_proj, material_proj))

                            cursor.execute("DELETE FROM INVENTORY WHERE MTL_CODE = %s "
                                           "AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                                           (material_ID, material_proj))
                            cursor.execute("UPDATE INVENTORY SET INVT_QTY = INVT_QTY + %s "
                                           "WHERE PROJ_ID IS NULL AND MTL_CODE = %s", (deleted_material, material_ID))

                            connection.commit()
                        connection.commit()
                self.load_materials()
                self.insert_materials()
            except Exception as e:
                print(e)

    def insert_materials(self):
        cur = connection.cursor()
        cur.execute("SELECT COALESCE(PROJ_NAME, 'Unassigned') "
                    "FROM MATERIAL  "
                    "LEFT JOIN INVENTORY USING (MTL_CODE)  "
                    "LEFT JOIN PROJECT USING (PROJ_ID) "
                    "GROUP BY PROJ_NAME "
                    "ORDER BY PROJ_NAME IS NULL DESC")
        update_proj = cur.fetchall()
        projs = [str(row[0]) for row in update_proj]
        self.update_material_projs_ddl.addItems(projs)

        # Fetch material names and populate drop-down list
        cur.execute("SELECT MTL_NAME "
                    "FROM MATERIAL  "
                    "LEFT JOIN INVENTORY USING (MTL_CODE)  "
                    "LEFT JOIN PROJECT USING (PROJ_ID) "
                    "GROUP BY MTL_NAME "
                    "ORDER BY MTL_NAME ASC")
        data_material = cur.fetchall()
        names = [str(row[0]) for row in data_material]
        self.update_materials_ddl.addItems(names)
        self.assign_materials_ddl.addItems(names)

        # Fetch material names and populate drop-down list
        cur.execute("SELECT PROJ_NAME FROM PROJECT WHERE PROJ_STATUS != 'Completed' GROUP BY PROJ_NAME")
        data_material = cur.fetchall()
        asg_projs = [str(row[0]) for row in data_material]
        self.assign_proj_ddl.addItems(asg_projs)

        # Fetch material count and sum of prices
        cur.execute(
            "SELECT COALESCE(SUM(INVT_QTY * MTL_PRICE), 0.00) FROM INVENTORY JOIN MATERIAL USING(MTL_CODE)")
        details = cur.fetchone()
        total_price = details[0]

        cur.execute(
            "SELECT COUNT(*) FROM MATERIAL ")
        details = cur.fetchone()
        material_count = details[0]

        # Set labels with the retrieved values
        self.label_total_num_material.setText("Total of Materials: " + str(material_count))
        self.label_total_material_price.setText(f"Total Materials Price: ₱{total_price:,.2f}")
        self.load_materials()
        cur.close()

    def load_materials(self):
        cur = connection.cursor()
        cur.execute("SELECT MTL_CODE, INVT_QTY, MTL_NAME, MTL_PRICE, COALESCE(PROJ_NAME, 'Unassigned') "
                    "FROM MATERIAL  "
                    "LEFT JOIN INVENTORY USING (MTL_CODE)  "
                    "LEFT JOIN PROJECT USING (PROJ_ID) "
                    "WHERE PROJ_STATUS != 'Completed' OR PROJ_STATUS IS NULL "
                    "ORDER BY PROJ_ID IS NULL DESC, PROJ_NAME")
        materials = cur.fetchall()

        self.tablewidget_materials_list.setRowCount(len(materials))

        for row_index, row_data in enumerate(materials):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_materials_list.setItem(row_index, column_index, item)

    def add_material(self):
        add_new_material = Inventory_AddMaterial_Admin()
        widget_stack.addWidget(add_new_material)
        widget_stack.setCurrentWidget(add_new_material)

    def go_to_equipment(self):
        inventory_equipment = Inventory_Equipment_Admin()
        widget_stack.addWidget(inventory_equipment)
        widget_stack.setCurrentWidget(inventory_equipment)

    def back_admin(self):
        admin_dashboard = AdminDashboardWindow()
        widget_stack.addWidget(admin_dashboard)
        widget_stack.setCurrentWidget(admin_dashboard)


class Inventory_AddMaterial_Admin(QDialog):
    def __init__(self):
        super(Inventory_AddMaterial_Admin, self).__init__()
        loadUi("InventoryListAddMaterial.ui", self)
        self.Label_user_name.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_material)
        self.button_add_new_material.clicked.connect(self.new_material)
        # self.material_id.setValidator(validator_int)
        self.material_quantity.setValidator(validator_int)
        self.material_price.setValidator(validator_float)

    def new_material(self):
        mtl_id = self.material_id.text()
        mtl_qty = self.material_quantity.text()
        mtl_name = self.material_name.text()
        mtl_price = self.material_price.text()
        if len(mtl_id) == 0 or len(mtl_qty) == 0 or len(mtl_name) == 0 or len(mtl_price) == 0:
            QMessageBox.information(self, "Incomplete Fields", "Please fill all the fields")
            return

        cur = connection.cursor()

        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to add this material",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                query = "INSERT INTO MATERIAL VALUES(%s,%s,%s)"
                cur.execute(query, (mtl_id, mtl_name, mtl_price))
                connection.commit()

                cur.execute("INSERT INTO INVENTORY (INVT_QTY, MTL_CODE) VALUES(%s, %s)", (mtl_qty, mtl_id))
                connection.commit()

                cur.close()
                self.back_material()
            except Exception:
                QMessageBox.information(self, "Material Exist", "Material already exist!")
                return

    def back_material(self):
        inventory_material = Inventory_Material_Admin()
        widget_stack.addWidget(inventory_material)
        widget_stack.setCurrentWidget(inventory_material)


class Inventory_Equipment_Admin(QDialog):
    def __init__(self):
        super(Inventory_Equipment_Admin, self).__init__()
        loadUi("InventoryListEquipment.ui", self)
        self.Label_admin_name.setText(Data.user_name)
        self.button_material_inventory.clicked.connect(self.go_to_inventory_materials)
        self.button_add_equipment.clicked.connect(self.add_equipment)
        self.backButton.clicked.connect(self.back_admin)
        self.button_delete_equipment.clicked.connect(self.delete_equipment)
        self.button_update_equipment.clicked.connect(self.update_quantity)
        self.button_assign_proj.clicked.connect(self.assign_equipment)
        self.equipment_update_quantity.setValidator(validator_int)
        self.assign_quantity_equipment.setValidator(validator_int)
        self.load_equipments()
        self.insert_equipments()

    def assign_equipment(self):
        # Retrieve selected project, equipment, and quantity
        asg_proj = self.assign_proj_ddl.currentText()
        asg_eqpt = self.assign_equipment_ddl.currentText()
        asg_qty = self.assign_quantity_equipment.text()

        if len(asg_qty) == 0:
            # Check if quantity is provided
            QMessageBox.information(self, "Blank field", "Please input a quantity")
            return
        cur = connection.cursor()

        # Check if equipment is already assigned to the project
        cur.execute(
            "SELECT EQPT_CODE FROM INVENTORY WHERE EQPT_CODE = (SELECT EQPT_CODE FROM EQUIPMENT WHERE EQPT_NAME = %s) AND "
            "PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)", (asg_eqpt, asg_proj))
        exist = cur.fetchall()
        if exist:
            QMessageBox.information(self, "Equipment Exist in Project",
                                    "The equipment is already assigned to the project.")
            return

        # Check if there is sufficient quantity in the inventory
        cur.execute(
            "SELECT INVT_QTY FROM INVENTORY WHERE PROJ_ID IS NULL AND EQPT_CODE = (SELECT EQPT_CODE FROM EQUIPMENT WHERE EQPT_NAME = %s)",
            (asg_eqpt,))
        check_qty = cur.fetchone()
        if check_qty[0] < int(asg_qty):
            QMessageBox.information(self, "Invalid Quantity",
                                    "Can't assign quantity. The material quantity is insufficient.")
            return

        # Update inventory quantity by subtracting assigned quantity
        cur.execute(
            "UPDATE INVENTORY SET INVT_QTY = INVT_QTY - %s WHERE PROJ_ID IS NULL AND EQPT_CODE = (SELECT EQPT_CODE FROM EQUIPMENT WHERE EQPT_NAME = %s)",
            (asg_qty, asg_eqpt))
        connection.commit()

        # Insert new inventory record with assigned quantity and project
        cur.execute("INSERT INTO INVENTORY(INVT_QTY, PROJ_ID, EQPT_CODE) "
                    "VALUES(%s, (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s), "
                    "(SELECT EQPT_CODE FROM EQUIPMENT WHERE EQPT_NAME = %s))", (asg_qty, asg_proj, asg_eqpt))
        connection.commit()
        try:
            # Update budget with the cost of the assigned equipment
            cur.execute("UPDATE BUDGET SET BDGT_COST = BDGT_COST + (SELECT INVT_QTY*EQPT_PRICE FROM EQUIPMENT "
                        "LEFT JOIN INVENTORY USING(EQPT_CODE) "
                        "LEFT JOIN PROJECT USING(PROJ_ID) "
                        "WHERE EQPT_NAME = %s AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)) "
                        "WHERE PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)", (asg_eqpt, asg_proj,asg_proj))
            connection.commit()

        except Exception as e:
            print(e)
            return

        # Display success message and clear input fields
        QMessageBox.information(self, "Assigned Successful", "The equipment is assigned to the certain project.")
        self.assign_quantity_equipment.clear()
        self.load_equipments()
        self.insert_equipments()

    def update_quantity(self):
        # Retrieve selected project, equipment, and new quantity
        proj_name = self.update_equipment_projs_ddl.currentText()
        eqpt_name = self.update_equipments_ddl.currentText()
        eqpt_qty = self.equipment_update_quantity.text()

        if len(eqpt_qty) == 0:
            # Check if quantity is provided
            QMessageBox.information(self, "No Quantity", "Enter Material Quantity")
            return

        cur = connection.cursor()

        # Check if there is sufficient quantity in the inventory for unassigned equipment
        cur.execute(
            "SELECT INVT_QTY FROM EQUIPMENT "
            "LEFT JOIN INVENTORY USING (EQPT_CODE) "
            "LEFT JOIN PROJECT USING (PROJ_ID) "
            "WHERE PROJ_ID IS NULL AND EQPT_NAME = %s", (eqpt_name,))

        unassigned_qty = cur.fetchone()

        if proj_name != "Unassigned" and unassigned_qty[0] < int(eqpt_qty):
            QMessageBox.information(
                self,
                "Invalid Quantity",
                "Can't subtract quantity. The material quantity is insufficient."
            )
            return

        # Check if equipment is assigned to the project
        cur.execute(
            "SELECT PROJ_ID FROM INVENTORY WHERE PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s) "
            "AND EQPT_CODE = "
            "(SELECT EQPT_CODE FROM EQUIPMENT WHERE EQPT_NAME = %s)", (proj_name, eqpt_name))
        proj_assigned = cur.fetchall()
        if proj_name != "Unassigned" and len(proj_assigned) == 0:
            QMessageBox.information(self, "Equipment not assigned",
                                    "The equipment is not assigned to the specified project.")
            return

        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Add the equipment quantity?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            try:

                if proj_name != "Unassigned":

                    # Subtract quantity from inventory and add to assigned project
                    cur.execute("UPDATE INVENTORY SET INVT_QTY = INVT_QTY - %s "
                                "WHERE PROJ_ID IS NULL "
                                "AND EQPT_CODE = (SELECT EQPT_CODE FROM EQUIPMENT WHERE EQPT_NAME = %s)",
                                (eqpt_qty, eqpt_name))
                    connection.commit()

                    cur.execute("UPDATE INVENTORY SET INVT_QTY = INVT_QTY + %s WHERE EQPT_CODE = "
                                "(SELECT EQPT_CODE FROM EQUIPMENT WHERE EQPT_NAME = %s) "
                                "AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                                (eqpt_qty, eqpt_name, proj_name))
                    connection.commit()
                    try:
                        # Update budget with the cost of the assigned equipment
                        cur.execute("UPDATE BUDGET SET BDGT_COST = BDGT_COST + (SELECT INVT_QTY*EQPT_PRICE FROM EQUIPMENT "
                                    "LEFT JOIN INVENTORY USING(EQPT_CODE) "
                                    "LEFT JOIN PROJECT USING(PROJ_ID) "
                                    "WHERE EQPT_NAME = %s AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)) "
                                    "WHERE PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                                    (eqpt_name, proj_name, proj_name))
                        connection.commit()
                    except Exception as e:
                        print(e)
                        return
                else:
                    # Add quantity to unassigned inventory
                    cur.execute("UPDATE INVENTORY SET INVT_QTY = INVT_QTY + %s WHERE PROJ_ID IS NULL AND EQPT_CODE = "
                                "(SELECT EQPT_CODE FROM EQUIPMENT WHERE EQPT_NAME = %s)", (eqpt_qty, eqpt_name))
                    connection.commit()
            except Exception as e:
                print(e)
            self.equipment_update_quantity.clear()
            self.load_equipments()
            self.insert_equipments()


    def delete_equipment(self):
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to delete this equipment?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            selected_row = self.tablewidget_Equipment_List.currentRow()
            if selected_row != -1:
                equipment_ID = self.tablewidget_Equipment_List.item(selected_row, 0).text()
                equipment_proj = self.tablewidget_Equipment_List.item(selected_row, 4).text()
                self.tablewidget_Equipment_List.removeRow(selected_row)

                with connection.cursor() as cursor:
                    if equipment_proj == "Unassigned":
                        cursor.execute("DELETE FROM INVENTORY WHERE EQPT_CODE = %s AND PROJ_ID IS NULL",
                                       (equipment_ID,))
                        cursor.execute("DELETE FROM EQUIPMENT WHERE EQPT_CODE = %s", (equipment_ID,))
                    else:
                        cursor.execute("SELECT INVT_QTY FROM INVENTORY WHERE EQPT_CODE = %s "
                                       "AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                                       (equipment_ID, equipment_proj))
                        deleted_equipment = cursor.fetchone()[0]
                        try:

                            cursor.execute(
                                "UPDATE BUDGET SET BDGT_COST = BDGT_COST - (SELECT INVT_QTY*EQPT_PRICE FROM EQUIPMENT "
                                "LEFT JOIN INVENTORY USING(EQPT_CODE) "
                                "LEFT JOIN PROJECT USING(PROJ_ID) "
                                "WHERE EQPT_CODE = %s AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)) "
                                "WHERE PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                                (equipment_ID, equipment_proj, equipment_proj))
                        except Exception as e:
                            print(e)
                            return

                    cursor.execute(
                            "DELETE FROM INVENTORY WHERE EQPT_CODE = %s AND PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s)",
                            (equipment_ID, equipment_proj))

                    cursor.execute("UPDATE INVENTORY SET INVT_QTY = INVT_QTY + %s "
                                   "WHERE PROJ_ID IS NULL AND EQPT_CODE = %s", (deleted_equipment, equipment_ID))

                    connection.commit()
            self.load_equipments()
            self.insert_equipments()

    def insert_equipments(self):
        cur = connection.cursor()
        cur.execute("SELECT COALESCE(PROJ_NAME, 'Unassigned') "
                    "FROM EQUIPMENT  "
                    "LEFT JOIN INVENTORY USING (EQPT_CODE)  "
                    "LEFT JOIN PROJECT USING (PROJ_ID) "
                    "GROUP BY PROJ_NAME "
                    "ORDER BY PROJ_NAME IS NULL DESC")
        update_proj = cur.fetchall()
        projs = [str(row[0]) for row in update_proj]
        self.update_equipment_projs_ddl.addItems(projs)

        # Fetch equipments names and populate drop-down list
        cur.execute("SELECT EQPT_NAME "
                    "FROM EQUIPMENT  "
                    "LEFT JOIN INVENTORY USING (EQPT_CODE)  "
                    "LEFT JOIN PROJECT USING (PROJ_ID) "
                    "GROUP BY EQPT_NAME "
                    "ORDER BY EQPT_NAME ASC")
        data_equipment = cur.fetchall()
        names = [str(row[0]) for row in data_equipment]
        self.update_equipments_ddl.addItems(names)
        self.assign_equipment_ddl.addItems(names)

        # Fetch equipments names and populate drop-down list
        cur.execute("SELECT PROJ_NAME FROM PROJECT WHERE PROJ_STATUS != 'Completed'")
        data_material = cur.fetchall()
        asg_projs = [str(row[0]) for row in data_material]
        self.assign_proj_ddl.addItems(asg_projs)

        # Fetch material count and sum of prices
        cur.execute(
            "SELECT COALESCE(SUM(INVT_QTY * EQPT_PRICE), 0.00) FROM INVENTORY JOIN EQUIPMENT USING(EQPT_CODE)")
        details = cur.fetchone()
        total_price = details[0]

        cur.execute(
            "SELECT COUNT(*) FROM EQUIPMENT ")
        details = cur.fetchone()
        equipment_count = details[0]

        # Set labels with the retrieved values
        self.label_total_num_quipments.setText("Total of Equipments: " + str(equipment_count))
        self.label_total_quipment_price.setText(f"Total Equipments Price: ₱{total_price:,.2f}")
        self.load_equipments()
        cur.close()

    def load_equipments(self):
        cur = connection.cursor()
        cur.execute("SELECT EQPT_CODE, INVT_QTY, EQPT_NAME, EQPT_PRICE, COALESCE(PROJ_NAME, 'Unassigned') "
                    "FROM EQUIPMENT  "
                    "LEFT JOIN INVENTORY USING (EQPT_CODE)  "
                    "LEFT JOIN PROJECT USING (PROJ_ID) "
                    "WHERE PROJ_STATUS != 'Completed' OR PROJ_STATUS IS NULL "
                    "ORDER BY PROJ_ID IS NULL DESC, PROJ_NAME")
        equipments = cur.fetchall()

        self.tablewidget_Equipment_List.setRowCount(len(equipments))

        for row_index, row_data in enumerate(equipments):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_Equipment_List.setItem(row_index, column_index, item)

    def add_equipment(self):
        add_new_equipment = Inventory_AddEquipment_Admin()
        widget_stack.addWidget(add_new_equipment)
        widget_stack.setCurrentWidget(add_new_equipment)

    def go_to_inventory_materials(self):
        inventory_material = Inventory_Material_Admin()
        widget_stack.addWidget(inventory_material)
        widget_stack.setCurrentWidget(inventory_material)

    def back_admin(self):
        admin_dashboard = AdminDashboardWindow()
        widget_stack.addWidget(admin_dashboard)
        widget_stack.setCurrentWidget(admin_dashboard)


class Inventory_AddEquipment_Admin(QDialog):
    def __init__(self):
        super(Inventory_AddEquipment_Admin, self).__init__()
        loadUi("InventoryListAddEquipment.ui", self)
        self.Label_user_name.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_equipment)
        self.button_add_new_equipment.clicked.connect(self.new_equipment)
        self.Equipment_Quantity.setValidator(validator_int)
        self.Equipment_Price.setValidator(validator_float)

    def new_equipment(self):
        eqpt_id = self.Equipment_ID.text()
        eqpt_qty = self.Equipment_Quantity.text()
        eqpt_name = self.Equipment_Name.text()
        eqpt_price = self.Equipment_Price.text()
        if len(eqpt_id) == 0 or len(eqpt_qty) == 0 or len(eqpt_name) == 0 or len(eqpt_price) == 0:
            QMessageBox.information(self, "Incomplete Fields", "Please fill all the fields")
            return

        cur = connection.cursor()

        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to add this equipment",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                query = "INSERT INTO EQUIPMENT VALUES(%s,%s,%s)"
                cur.execute(query, (eqpt_id, eqpt_name, eqpt_price))
                connection.commit()

                cur.execute("INSERT INTO INVENTORY (INVT_QTY, EQPT_CODE) VALUES(%s, %s)", (eqpt_qty, eqpt_id))
                connection.commit()

                cur.close()
                self.back_equipment()
            except Exception:
                QMessageBox.information(self, "Equipment Exist",
                                        "Equipment already exist!. Enter a unique Code or Name.")
                return

    def back_equipment(self):
        inventory_equipment = Inventory_Equipment_Admin()
        widget_stack.addWidget(inventory_equipment)
        widget_stack.setCurrentWidget(inventory_equipment)


class Admin_Project(QDialog):
    def __init__(self):
        super(Admin_Project, self).__init__()
        loadUi("Admin_Project.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.button_new_proj.clicked.connect(self.go_to_add_proj)
        self.button_ongoing_proj.clicked.connect(self.go_to_ongoings)
        self.button_accomplished_proj.clicked.connect(self.go_to_accomplish)
        self.backButton.clicked.connect(self.back_admin)
        self.button_search.clicked.connect(self.search_project_ID)
        self.button_load_project.clicked.connect(self.load_projects)
        self.button_complete.clicked.connect(self.complete_proj)
        self.search_project.setValidator(validator_int)
        self.load_projects()

    def complete_proj(self):
        # Confirmation to complete the new project
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Is this project is finished?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        # Get the ID of the selected project from the table
        if confirmation == QMessageBox.StandardButton.Yes:
            selected_row = self.table_projects.currentRow()
            if selected_row != -1:
                proj_id = self.table_projects.item(selected_row, 0).text()
                self.table_projects.removeRow(selected_row)

                with connection.cursor() as cursor:
                    # Update the status of the completed project
                    cursor.execute(
                        "UPDATE PROJECT SET PROJ_STATUS = 'Completed' WHERE PROJ_ID = %s",
                        (proj_id,))
                    cursor.execute("UPDATE EMPLOYEE SET PAY_ID = NULL WHERE PROJ_ID = %s", (proj_id,))
                    connection.commit()
                self.load_projects()

    def search_project_ID(self):
        proj_id = self.search_project.text()

        # Check if the field inputted is empty
        if len(proj_id) == 0:
            QMessageBox.information(self, "Empty ID", "Please enter a valid ID")
            return

        cur = connection.cursor()
        # Check if the ID is not existed
        cur.execute("SELECT * FROM PROJECT WHERE PROJ_ID = %s", (proj_id,))
        projects = cur.fetchall()

        if not projects:
            QMessageBox.information(self, "Project not exist", "Please enter a valid ID")
            return

        # Load the tables base on the inputted field
        self.table_projects.setRowCount(len(projects))
        index = 0
        for i in projects:
            self.table_projects.setItem(index, 0, QtWidgets.QTableWidgetItem(str(i[0])))
            self.table_projects.setItem(index, 1, QtWidgets.QTableWidgetItem(str(i[1])))
            self.table_projects.setItem(index, 2, QtWidgets.QTableWidgetItem(str(i[2])))
            self.table_projects.setItem(index, 3, QtWidgets.QTableWidgetItem(str(i[3])))
            self.table_projects.setItem(index, 4, QtWidgets.QTableWidgetItem(str(i[4])))
            self.table_projects.setItem(index, 5, QtWidgets.QTableWidgetItem(str(i[5])))
            self.table_projects.setItem(index, 6, QtWidgets.QTableWidgetItem(str(i[-1])))
            index += 1
        cur.close()

    def load_projects(self):
        # Load all the projects
        cur = connection.cursor()
        cur.execute("SELECT * FROM PROJECT ORDER BY PROJ_STATUS DESC")
        projects = cur.fetchall()
        self.table_projects.setRowCount(len(projects))
        index = 0
        for i in projects:
            self.table_projects.setItem(index, 0, QtWidgets.QTableWidgetItem(str(i[0])))
            self.table_projects.setItem(index, 1, QtWidgets.QTableWidgetItem(str(i[1])))
            self.table_projects.setItem(index, 2, QtWidgets.QTableWidgetItem(str(i[2])))
            self.table_projects.setItem(index, 3, QtWidgets.QTableWidgetItem(str(i[3])))
            self.table_projects.setItem(index, 4, QtWidgets.QTableWidgetItem(str(i[4])))
            self.table_projects.setItem(index, 5, QtWidgets.QTableWidgetItem(str(i[5])))
            self.table_projects.setItem(index, 6, QtWidgets.QTableWidgetItem(str(i[-1])))
            index += 1
        cur.close()

    def go_to_ongoings(self):
        ongoings = Admin_Ongoings_Project()
        widget_stack.addWidget(ongoings)
        widget_stack.setCurrentWidget(ongoings)

    def go_to_accomplish(self):
        accomplish = Admin_Accomplished_Project()
        widget_stack.addWidget(accomplish)
        widget_stack.setCurrentWidget(accomplish)

    def go_to_add_proj(self):
        add_project = Admin_Add_Project()
        widget_stack.addWidget(add_project)
        widget_stack.setCurrentWidget(add_project)

    def back_admin(self):
        admin_dashboard = AdminDashboardWindow()
        widget_stack.addWidget(admin_dashboard)
        widget_stack.setCurrentWidget(admin_dashboard)


class Admin_Add_Project(QDialog):
    def __init__(self):
        super(Admin_Add_Project, self).__init__()
        loadUi("Admin_New_Project.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.button_save_proj.clicked.connect(self.save_project)
        self.backButton.clicked.connect(self.back_project)
        self.proj_id.setValidator(validator_int)
        self.insert_leaders()

    def save_project(self):
        # Get the entered fields
        proj_id = self.proj_id.text()
        proj_name = self.proj_name.text()
        proj_address = self.proj_address.text()
        proj_start = self.proj_start.date().toString(QtCore.Qt.DateFormat.ISODate)
        proj_end = self.proj_end.date().toString(QtCore.Qt.DateFormat.ISODate)
        proj_leader = self.leader_ddl.currentText()

        # Vaalidate the fields if there's empty
        if len(proj_id) == 0 or len(proj_name) == 0 or len(proj_address) == 0:
            QMessageBox.information(self, "Blank Fields", "PLease fill all fields.")
            return

        cur = connection.cursor()

        if proj_start >= proj_end:
            QMessageBox.information(self, "Invalid Dates", "Project end date should be after the start date.")
            return

        # Confirmation to save a project
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Save Project?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                # Add the new project
                query = "INSERT INTO PROJECT(PROJ_ID, PROJ_NAME, PROJ_ADDRESS, PROJ_START, PROJ_END, PROJ_LEADER)" \
                        " VALUES(%s, %s, %s, %s, %s, %s) RETURNING PROJ_ID"
                cur.execute(query, (proj_id, proj_name, proj_address, proj_start, proj_end, proj_leader))
                new_proj_id = cur.fetchone()[0]
                connection.commit()
                cur.execute("INSERT INTO BUDGET(PROJ_ID) VALUES(%s)", (new_proj_id,))
                connection.commit()

                cur.close()
                QMessageBox.information(self, "Saved Project", "New Project is successfuly saved.")
                self.back_project()
            except Exception:
                # Display and return if the project is already exist
                QMessageBox.information(self, "Project Exist",
                                        "Please enter a new unique project name or unique project ID.")
                return

    def insert_leaders(self):
        cur = connection.cursor()

        # Fetch material names and populate drop-down list
        cur.execute(
            "SELECT USER_ID FROM USER_LOG LEFT JOIN PROJECT ON USER_ID = PROJ_LEADER WHERE PROJ_STATUS IS NULL OR PROJ_STATUS != 'Ongoing'")
        leaders = cur.fetchall()
        names = [str(row[0]) for row in leaders]
        self.leader_ddl.addItems(names)

        cur.close()

    def back_project(self):
        project = Admin_Project()
        widget_stack.addWidget(project)
        widget_stack.setCurrentWidget(project)


class Admin_Ongoings_Project(QDialog):
    def __init__(self):
        super(Admin_Ongoings_Project, self).__init__()
        loadUi("Admin_Ongoings_Project.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.button_show_details.clicked.connect(self.display_details)
        self.backButton.clicked.connect(self.back_project)
        self.all_projects()

    def display_details(self):
        try:
            # Retrieves and displays details of the selected project
            proj = self.projects_ddl.currentText()
            cur = connection.cursor()

            # Fetch project details from the database
            cur.execute("SELECT PROJ_ID, PROJ_NAME, PROJ_ADDRESS, PROJ_START, PROJ_END, "
                        "COUNT(EMP_ID), COUNT(MTL_CODE), COUNT(EQPT_CODE), USER_NAME FROM PROJECT P "
                        "LEFT JOIN EMPLOYEE USING(PROJ_ID) "
                        "LEFT JOIN INVENTORY USING(PROJ_ID) "
                        "LEFT JOIN USER_LOG U ON P.PROJ_LEADER = U.USER_ID "
                        "WHERE PROJ_STATUS = 'Ongoing' AND PROJ_NAME = %s "
                        "GROUP BY PROJ_ID, PROJ_NAME, PROJ_ADDRESS, PROJ_START, PROJ_END, USER_NAME ", (proj,))
            proj_details = cur.fetchone()

            # Fetch the project cost from the budget table
            cur.execute("SELECT BDGT_COST FROM BUDGET "
                        "JOIN PROJECT USING(PROJ_ID) "
                        "WHERE PROJ_STATUS = 'Ongoing' AND PROJ_NAME = %s", (proj,))
            cost = cur.fetchone()[0]

            # Display the project details and cost on the UI
            self.label_project_id.setText(str(proj_details[0]))
            self.label_project_name.setText(str(proj_details[1]))
            self.label_project_address.setText(str(proj_details[2]))
            self.label_project_start.setText(str(proj_details[3]))
            self.label_project_deadline.setText(str(proj_details[4]))
            self.label_personnels.setText(str(proj_details[5]))
            self.label_project_materials.setText(str(proj_details[6]))
            self.label_project_equipments.setText(str(proj_details[7]))
            self.label_project_leader.setText(str(proj_details[8]))
            self.label_project_budget.setText("₱{:,.2f}".format(cost))

            # Update the assigned materials and equipments tables
            self.assigned_materials()
            self.assigned_equipments()

        except Exception:
            QMessageBox.information(self, "No Project Selected", "Select Project.")

    def all_projects(self):
        # Fetch all ongoing projects from the database and populate the dropdown list
        cur = connection.cursor()
        cur.execute("SELECT PROJ_NAME FROM PROJECT WHERE PROJ_STATUS = 'Ongoing'")
        ongoings_projs = cur.fetchall()
        projs = [str(row[0]) for row in ongoings_projs]
        self.projects_ddl.addItems(projs)

    def assigned_materials(self):
        try:
            # Display the materials assigned to the selected project
            proj = self.projects_ddl.currentText()
            cur = connection.cursor()

            cur.execute("SELECT MTL_CODE, MTL_NAME, INVT_QTY, INVT_QTY * MTL_PRICE "
                        "FROM INVENTORY I "
                        "LEFT JOIN MATERIAL USING(MTL_CODE) "
                        "LEFT JOIN PROJECT USING(PROJ_ID) "
                        "WHERE PROJ_NAME = %s AND MTL_CODE IS NOT NULL AND PROJ_STATUS = 'Ongoing'", (proj,))
            mtl = cur.fetchall()

            # Calculate the total cost of assigned materials
            total_cost = sum(item[3] for item in mtl if item[3] is not None)
            self.lbl_mtl_cost.setText(f"Equipments Total Cost: ₱{float(total_cost or 0):,.2f}")

            # Update the table with the assigned materials
            self.table_used_materials.setRowCount(len(mtl))

            for row_index, row_data in enumerate(mtl):
                for column_index, column_data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(column_data))
                    self.table_used_materials.setItem(row_index, column_index, item)

        except Exception:
            QMessageBox.information(self, "No Project Selected", "Select Project.")

    def assigned_equipments(self):
        try:
            # Display the equipments assigned to the selected project
            proj = self.projects_ddl.currentText()
            cur = connection.cursor()

            cur.execute("SELECT EQPT_CODE, EQPT_NAME, INVT_QTY, INVT_QTY * EQPT_PRICE "
                        "FROM INVENTORY I "
                        "LEFT JOIN EQUIPMENT USING(EQPT_CODE) "
                        "LEFT JOIN PROJECT USING(PROJ_ID) "
                        "WHERE PROJ_NAME = %s AND EQPT_CODE IS NOT NULL AND PROJ_STATUS = 'Ongoing'", (proj,))
            eqpt = cur.fetchall()

            # Calculate the total cost of assigned equipments
            total_cost = sum(item[3] for item in eqpt if item[3] is not None)
            self.lbl_eqpt_cost.setText(f"Materials Total Cost: ₱{float(total_cost or 0):,.2f}")

            # Update the table with the assigned equipments
            self.table_used_equipments.setRowCount(len(eqpt))

            for row_index, row_data in enumerate(eqpt):
                for column_index, column_data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(column_data))
                    self.table_used_equipments.setItem(row_index, column_index, item)

        except Exception:
            QMessageBox.information(self, "No Project Selected", "Select Project.")

    def back_project(self):
        project = Admin_Project()
        widget_stack.addWidget(project)
        widget_stack.setCurrentWidget(project)


class Admin_Accomplished_Project(QDialog):
    def __init__(self):
        super(Admin_Accomplished_Project, self).__init__()
        loadUi("Admin_Accomplished_Project.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.button_show_details.clicked.connect(self.display_details)
        self.backButton.clicked.connect(self.back_project)
        self.all_projects()

    def display_details(self):
        try:
            # Retrieve the selected project from the drop-down list
            proj = self.projects_ddl.currentText()
            cur = connection.cursor()

            # Query the database to fetch project details and associated personnel, materials, and equipment
            cur.execute("SELECT PROJ_ID, PROJ_NAME, PROJ_ADDRESS, PROJ_START, PROJ_END, "
                        "COUNT(EMP_ID), COUNT(MTL_CODE), COUNT(EQPT_CODE), USER_NAME FROM PROJECT P "
                        "LEFT JOIN EMPLOYEE USING(PROJ_ID) "
                        "LEFT JOIN INVENTORY USING(PROJ_ID) "
                        "LEFT JOIN USER_LOG U ON P.PROJ_LEADER = U.USER_ID "
                        "WHERE PROJ_STATUS = 'Completed' AND PROJ_NAME = %s "
                        "GROUP BY PROJ_ID, PROJ_NAME, PROJ_ADDRESS, PROJ_START, PROJ_END, USER_NAME ", (proj,))
            proj_details = cur.fetchone()

            # Fetch the project cost from the BUDGET table
            cur.execute("SELECT BDGT_COST FROM BUDGET "
                        "JOIN PROJECT USING(PROJ_ID) "
                        "WHERE PROJ_STATUS = 'Completed' AND PROJ_NAME = %s", (proj,))
            cost = cur.fetchone()[0]

            # Update the UI labels with the retrieved project details and cost
            self.label_project_id.setText(str(proj_details[0]))
            self.label_project_name.setText(str(proj_details[1]))
            self.label_project_address.setText(str(proj_details[2]))
            self.label_project_start.setText(str(proj_details[3]))
            self.label_project_deadline.setText(str(proj_details[4]))
            self.label_personnels.setText(str(proj_details[5]))
            self.label_project_materials.setText(str(proj_details[6]))
            self.label_project_equipments.setText(str(proj_details[7]))
            self.label_project_leader.setText(str(proj_details[8]))
            self.label_project_budget.setText("₱{:,.2f}".format(cost))

            # Display the associated materials and equipments in tables
            self.assigned_materials()
            self.assigned_equipments()

        except Exception:
            QMessageBox.information(self, "No Project Selected", "Select Project.")

    def all_projects(self):
        cur = connection.cursor()
        # Fetch the names of completed projects from the database
        cur.execute("SELECT PROJ_NAME FROM PROJECT WHERE PROJ_STATUS = 'Completed'")
        ongoings_projs = cur.fetchall()
        projs = [str(row[0]) for row in ongoings_projs]
        # Populate the drop-down list in the UI with the project names
        self.projects_ddl.addItems(projs)

    def assigned_materials(self):
        try:
            proj = self.projects_ddl.currentText()
            cur = connection.cursor()

            # Retrieve the materials associated with the selected project
            cur.execute("SELECT MTL_CODE, MTL_NAME, INVT_QTY, INVT_QTY * MTL_PRICE "
                        "FROM INVENTORY I "
                        "LEFT JOIN MATERIAL USING(MTL_CODE) "
                        "LEFT JOIN PROJECT USING(PROJ_ID) "
                        "WHERE PROJ_NAME = %s AND MTL_CODE IS NOT NULL AND PROJ_STATUS = 'Completed'", (proj,))
            mtl = cur.fetchall()

            # Calculate the total cost of the equipment
            total_cost = sum(item[3] for item in mtl if item[3] is not None)
            self.lbl_mtl_cost.setText(f"Equipments Total Cost: ₱{float(total_cost or 0):,.2f}")

            # Display the equipment in a table
            self.table_used_materials.setRowCount(len(mtl))

            for row_index, row_data in enumerate(mtl):
                for column_index, column_data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(column_data))
                    self.table_used_materials.setItem(row_index, column_index, item)

        except Exception:
            QMessageBox.information(self, "No Project Selected", "Select Project.")

    def assigned_equipments(self):
        try:
            proj = self.projects_ddl.currentText()
            cur = connection.cursor()

            # Retrieve the equpments associated with the selected project
            cur.execute("SELECT EQPT_CODE, EQPT_NAME, INVT_QTY, INVT_QTY * EQPT_PRICE "
                        "FROM INVENTORY I "
                        "LEFT JOIN EQUIPMENT USING(EQPT_CODE) "
                        "LEFT JOIN PROJECT USING(PROJ_ID) "
                        "WHERE PROJ_NAME = %s AND EQPT_CODE IS NOT NULL AND PROJ_STATUS = 'Completed'", (proj,))
            eqpt = cur.fetchall()

            # Calculate the total cost of the equipment
            total_cost = sum(item[3] for item in eqpt if item[3] is not None)
            self.lbl_eqpt_cost.setText(f"Materials Total Cost: ₱{float(total_cost or 0):,.2f}")

            # Display the equipment in a table
            self.table_used_equipments.setRowCount(len(eqpt))

            for row_index, row_data in enumerate(eqpt):
                for column_index, column_data in enumerate(row_data):
                    item = QtWidgets.QTableWidgetItem(str(column_data))
                    self.table_used_equipments.setItem(row_index, column_index, item)

        except Exception:
            QMessageBox.information(self, "No Project Selected", "Select Project.")

    def back_project(self):
        project = Admin_Project()
        widget_stack.addWidget(project)
        widget_stack.setCurrentWidget(project)


class Admin_Assign_Employee_Proj(QDialog):
    def __init__(self):
        super(Admin_Assign_Employee_Proj, self).__init__()
        loadUi("Admin_Project_Assigning.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_employees)
        self.button_refresh.clicked.connect(self.assign_table)
        self.button_filter.clicked.connect(self.filter_table)
        self.button_assign.clicked.connect(self.assign_employee)
        self.assign_employee_id.setValidator(validator_int)
        self.assign_table()
        self.load_ddl()

    def assign_employee(self):
        # Get the entered employee ID and selected project from the UI
        id = self.assign_employee_id.text()
        asg_proj = self.assign_project_ddl.currentText()
        cur = connection.cursor()

        if len(id) == 0:
            QMessageBox.information(self, "Employee not found", "Employee ID does not exist.")
            return

        # Check if the employee ID exists and is not inactive
        cur.execute("SELECT * FROM EMPLOYEE WHERE EMP_ID = %s AND EMP_STATUS != 'Inactive'", (id,))
        exist = cur.fetchone()

        if not exist:
            QMessageBox.information(self, "Employee not found", "Employee ID does not exist.")
            return

        # Check if the employee is already assigned to a project
        cur.execute("SELECT * FROM EMPLOYEE JOIN PROJECT USING (PROJ_ID) WHERE EMP_ID = %s AND PROJ_ID IS NOT NULL",
                    (id,))
        asg_exist = cur.fetchall()

        if asg_exist:
            # Ask for confirmation to reassign the employee
            confirmation = QMessageBox.question(
                self,
                "Employee already assigned",
                "Do you want to reassign this employee?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirmation == QMessageBox.StandardButton.Yes:
                # Reassign the employee to the selected project
                cur.execute(
                    "UPDATE EMPLOYEE SET PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s) WHERE EMP_ID = %s",
                    (asg_proj, id))
                connection.commit()
                QMessageBox.information(self, "Employee reassigned",
                                        "Employee has been reassigned to the selected project.")
                self.assign_table()
            else:
                return
        else:
            # Assign the employee to the selected project
            cur.execute(
                "UPDATE EMPLOYEE SET PROJ_ID = (SELECT PROJ_ID FROM PROJECT WHERE PROJ_NAME = %s) WHERE EMP_ID = %s",
                (asg_proj, id))
            connection.commit()
            QMessageBox.information(self, "Assignment success", "Employee assignment to project successfully.")
            self.assign_table()

        # Update payroll for the employee by setting salary and days of work to 0
        cur.execute("UPDATE PAYROLL SET PAY_SALARY = 0, PAY_DOW = 0 WHERE PAY_ID = (SELECT PAY_ID FROM PAYROLL "
                    "LEFT JOIN EMPLOYEE USING(PAY_ID) "
                    "WHERE EMP_ID = %s)", (id,))

    def load_ddl(self):
        cur = connection.cursor()

        # Fetch all project names and populate drop-down list
        cur.execute("SELECT PROJ_NAME FROM PROJECT")
        data_proj = cur.fetchall()
        names = [str(row[0]) for row in data_proj]
        self.projects_ddl.addItems(names)

        # Fetch unfinished projects and populate drop-down list
        cur.execute("SELECT PROJ_NAME FROM PROJECT WHERE PROJ_STATUS != 'Completed'")
        data_unproj = cur.fetchall()
        unproj = [str(row[0]) for row in data_unproj]
        self.assign_project_ddl.addItems(unproj)

    def filter_table(self):
        # Filter and display assigned employees for the selected project
        proj = self.projects_ddl.currentText()
        cur = connection.cursor()
        cur.execute("SELECT EMP_ID, (EMP_FNAME || ' ' || EMP_MNAME || ' ' || EMP_LNAME), "
                    "EMP_GENDER, EMP_AGE, EMP_POSITION, EMP_STATUS, PROJ_NAME "
                    "FROM EMPLOYEE LEFT JOIN PROJECT USING (PROJ_ID) "
                    "WHERE PROJ_NAME = %s AND EMP_STATUS != 'Inactive'", (proj,))
        asg_employees = cur.fetchall()

        self.tablewidget_assigned.setRowCount(len(asg_employees))

        for row_index, row_data in enumerate(asg_employees):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_assigned.setItem(row_index, column_index, item)

    def assign_table(self):
        # Display all employees and their assignments in a table
        cur = connection.cursor()
        cur.execute("SELECT EMP_ID, (EMP_FNAME || ' ' || EMP_MNAME || ' ' || EMP_LNAME), "
                    "EMP_GENDER, EMP_AGE, EMP_POSITION, EMP_STATUS, COALESCE(PROJ_NAME, 'Unassigned')"
                    "FROM EMPLOYEE LEFT JOIN PROJECT USING (PROJ_ID) "
                    "WHERE EMP_STATUS != 'Inactive'"
                    "ORDER BY PROJ_NAME IS NULL, PROJ_NAME ASC")
        employees = cur.fetchall()

        self.tablewidget_assigned.setRowCount(len(employees))

        for row_index, row_data in enumerate(employees):
            for column_index, column_data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(column_data))
                self.tablewidget_assigned.setItem(row_index, column_index, item)

    def back_employees(self):
        emp_list = Admin_EmployeeList()
        widget_stack.addWidget(emp_list)
        widget_stack.setCurrentWidget(emp_list)

class AdminAccounts(QDialog):
    def __init__(self):
        super(AdminAccounts, self).__init__()
        loadUi("AdminAccs.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_admin)
        self.button_load.clicked.connect(self.load_tables)
        self.load_tables()

        # Suspend Accounts
        self.button_suspend_admin.clicked.connect(self.suspend_admin)
        self.button_suspend_user.clicked.connect(self.suspend_user)

        # Unsuspend Accounts
        self.button_unsuspend_admin.clicked.connect(self.unsuspend_admin)
        self.button_unsuspend_user.clicked.connect(self.unsuspend_user)

        # Remove Accounts
        self.remove_admin_button.clicked.connect(self.remove_admin)
        self.remove_user_button.clicked.connect(self.remove_user)

        # Add new accounts
        self.add_admin_button.clicked.connect(self.go_to_new_admin)
        self.add_user_button.clicked.connect(self.go_to_new_user)

        # Update accounts
        self.button_update_admin.clicked.connect(self.go_to_update_admin)
        self.button_update_user.clicked.connect(self.go_to_update_user)

    # Methods for suspending, unsuspending, and removing admin and user accounts

    def suspend_admin(self):
        # Confirmation dialog
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to suspend this admin account?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            # Suspend the selected admin account
            selected_row = self.admin_tablewidget.currentRow()
            if selected_row != -1:
                admin_ID = self.admin_tablewidget.item(selected_row, 0).text()
                self.admin_tablewidget.removeRow(selected_row)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE ADMIN_LOG SET ADMIN_STATUS = 'Suspend' WHERE ADMIN_ID = %s AND ADMIN_STATUS != 'Inactive'",
                        (admin_ID,))
                    connection.commit()
                return

        self.load_tables()

    def suspend_user(self):
        # Confirmation dialog
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to suspend this user account?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            # Suspend the selected user account
            selected_row = self.user_tablewidget.currentRow()
            if selected_row != -1:
                user_ID = self.user_tablewidget.item(selected_row, 0).text()
                self.user_tablewidget.removeRow(selected_row)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE USER_LOG SET USER_STATUS = 'Suspend' WHERE USER_ID = %s AND USER_STATUS != 'Inactive'",
                        (user_ID,))
                    connection.commit()
                return

        self.load_tables()

    def unsuspend_admin(self):
        # Confirmation dialog
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to unsuspend this admin account?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            # Unsuspend the selected admin account
            selected_row = self.admin_tablewidget.currentRow()
            if selected_row != -1:
                admin_ID = self.admin_tablewidget.item(selected_row, 0).text()
                self.admin_tablewidget.removeRow(selected_row)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE ADMIN_LOG SET ADMIN_STATUS = 'Active' WHERE ADMIN_ID = %s AND ADMIN_STATUS != 'Inactive'",
                        (admin_ID,))
                    connection.commit()
                return

        self.load_tables()

    def unsuspend_user(self):
        # Confirmation dialog
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to unsuspend this user account?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            # Unsuspend the selected admin account
            selected_row = self.user_tablewidget.currentRow()
            if selected_row != -1:
                user_ID = self.user_tablewidget.item(selected_row, 0).text()
                self.user_tablewidget.removeRow(selected_row)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE USER_LOG SET USER_STATUS = 'Active' WHERE USER_ID = %s AND USER_STATUS != 'Inactive'",
                        (user_ID,))
                    connection.commit()
                return

        self.load_tables()

    def remove_admin(self):
        # Confirmation dialog
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to remove this admin account?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            # Remove the selected admin account
            selected_row = self.admin_tablewidget.currentRow()
            if selected_row != -1:
                admin_ID = self.admin_tablewidget.item(selected_row, 0).text()
                self.admin_tablewidget.removeRow(selected_row)

                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE ADMIN_LOG SET ADMIN_STATUS = 'Inactive' WHERE ADMIN_ID = %s",
                        (admin_ID,))
                    connection.commit()
                return

            self.load_tables()

    def remove_user(self):
        # Confirmation dialog
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to remove this user account?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmation == QMessageBox.StandardButton.Yes:
            # Remove the selected user account
            selected_row = self.user_tablewidget.currentRow()
            if selected_row != -1:
                user_ID = self.user_tablewidget.item(selected_row, 0).text()
                self.user_tablewidget.removeRow(selected_row)

                with connection.cursor() as cursor:
                    cursor.execute("UPDATE USER_LOG SET USER_STATUS = 'Inactive' WHERE USER_ID = %s", (user_ID,))
                    connection.commit()
                return

            self.load_tables()

    # Load all tables
    def load_tables(self):
        # Load admin accounts table
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM ADMIN_LOG WHERE ADMIN_STATUS != 'Inactive'")
        admin_rows = cursor.fetchall()

        self.admin_tablewidget.setRowCount(len(admin_rows))
        index = 0
        for i in admin_rows:
            # Populate the admin table with data
            self.admin_tablewidget.setItem(index, 0, QtWidgets.QTableWidgetItem(str(i[0])))
            self.admin_tablewidget.setItem(index, 1, QtWidgets.QTableWidgetItem(str(i[1])))
            self.admin_tablewidget.setItem(index, 2, QtWidgets.QTableWidgetItem(str(i[2])))
            self.admin_tablewidget.setItem(index, 3, QtWidgets.QTableWidgetItem(str(i[3])))
            self.admin_tablewidget.setItem(index, 4, QtWidgets.QTableWidgetItem(str(i[5])))
            self.admin_tablewidget.setItem(index, 5, QtWidgets.QTableWidgetItem(str(i[6])))
            self.admin_tablewidget.setItem(index, 6, QtWidgets.QTableWidgetItem(str(i[7])))
            index += 1
        cursor.close()

        # user Accounts table
        # Load user accounts table
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM USER_LOG WHERE USER_STATUS != 'Inactive'")
        user_rows = cursor.fetchall()

        self.user_tablewidget.setRowCount(len(user_rows))
        index = 0
        for i in user_rows:
            # Populate the user table with data
            self.user_tablewidget.setItem(index, 0, QtWidgets.QTableWidgetItem(str(i[0])))
            self.user_tablewidget.setItem(index, 1, QtWidgets.QTableWidgetItem(str(i[1])))
            self.user_tablewidget.setItem(index, 2, QtWidgets.QTableWidgetItem(str(i[2])))
            self.user_tablewidget.setItem(index, 3, QtWidgets.QTableWidgetItem(str(i[3])))
            self.user_tablewidget.setItem(index, 4, QtWidgets.QTableWidgetItem(str(i[5])))
            self.user_tablewidget.setItem(index, 5, QtWidgets.QTableWidgetItem(str(i[6])))
            self.user_tablewidget.setItem(index, 6, QtWidgets.QTableWidgetItem(str(i[7])))
            self.user_tablewidget.setItem(index, 7, QtWidgets.QTableWidgetItem(str(i[8])))
            index += 1
        cursor.close()

    def go_to_new_admin(self):
        new_admin = AdminAccounts_NewAdmin()
        widget_stack.addWidget(new_admin)
        widget_stack.setCurrentWidget(new_admin)

    def go_to_new_user(self):
        new_user = AdminAccounts_NewUser()
        widget_stack.addWidget(new_user)
        widget_stack.setCurrentWidget(new_user)

    def go_to_update_admin(self):
        update_admin = AdminAccounts_UpdateAdmin()
        widget_stack.addWidget(update_admin)
        widget_stack.setCurrentWidget(update_admin)

    def go_to_update_user(self):
        update_user = AdminAccounts_UpdateUser()
        widget_stack.addWidget(update_user)
        widget_stack.setCurrentWidget(update_user)

    def back_admin(self):
        admin_dashboard = AdminDashboardWindow()
        widget_stack.addWidget(admin_dashboard)
        widget_stack.setCurrentWidget(admin_dashboard)


class AdminAccounts_NewAdmin(QDialog):
    def __init__(self):
        super(AdminAccounts_NewAdmin, self).__init__()
        loadUi("AdminAccs_newAdmin.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_AdminAccounts)
        self.new_admin_button.clicked.connect(self.add_admin)
        self.admin_ID_input.setValidator(validator_int)

    def add_admin(self):
        # Retrieve admin input from QLineEdit widgets
        admin_id = self.admin_ID_input.text()
        admin_name = self.admin_name_input.text().replace(" ", "")
        admin_position = self.admin_position_input.text().replace(" ", "")
        admin_username = self.admin_username_input.text().replace(" ", "")
        admin_pass = self.admin_newpassword_input.text().replace(" ", "")
        admin_comfirm_pass = self.admin_confirmpassword_input.text().replace(" ", "")

        # Validate and process admin input
        if admin_pass != admin_comfirm_pass:
            # Show a warning message if passwords don't match
            QMessageBox.warning(self, "Unmatched Password", "Please match the password.")
            return
        elif len(admin_id) == 0 or len(admin_name) == 0 or len(admin_position) == 0 or len(admin_username) == 0 or len(
                admin_pass) == 0:
            # Show an error message if any field is empty
            QMessageBox.critical(self, "Fill all the fields", "Please fill all the fields!")
            return
        else:
            cur = connection.cursor()

            # Check if the admin_id or admin_username already exists and is active
            cur.execute("SELECT * FROM ADMIN_LOG WHERE (ADMIN_ID = %s OR ADMIN_USERNAME = %s) AND ADMIN_STATUS != 'Inactive'", (admin_id, admin_username))
            existing_admin = cur.fetchone()

            if existing_admin is None:
                # Add the new admin account
                query = "INSERT INTO ADMIN_LOG (ADMIN_ID, ADMIN_NAME, ADMIN_POSITION, ADMIN_USERNAME, ADMIN_PASSWORD) " \
                        "VALUES (%s, %s, %s, %s, %s)"
                cur.execute(query, (admin_id, admin_name, admin_position, admin_username, admin_pass))
                connection.commit()
                cur.close()
                QMessageBox.information(self, "New  Admin Account Added", "New Account Successfully Added")
                self.back_AdminAccounts()
            else:
                # Show a message if the admin account already exists
                QMessageBox.information(self, "Admin Account Exists", "Admin account already exists!")
                cur.close()
                return

            # Clear the text in the QLineEdit widgets
            self.admin_ID_input.clear()
            self.admin_name_input.clear()
            self.admin_position_input.clear()
            self.admin_username_input.clear()
            self.admin_newpassword_input.clear()
            self.admin_confirmpassword_input.clear()

    def back_AdminAccounts(self):
        admin_accounts = AdminAccounts()
        widget_stack.addWidget(admin_accounts)
        widget_stack.setCurrentWidget(admin_accounts)


class AdminAccounts_NewUser(QDialog):
    def __init__(self):
        super(AdminAccounts_NewUser, self).__init__()
        loadUi("AdminAccs_newUser.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_AdminAccounts)
        self.new_admin_button.clicked.connect(self.add_user)
        self.user_ID_input.setValidator(validator_int)

    def add_user(self):
        # Retrieve user input from QLineEdit widgets
        user_id = self.user_ID_input.text().replace(" ", "")
        user_name = self.user_name_input.text().replace(" ", "")
        user_position = self.user_position_input.text().replace(" ", "")
        user_username = self.user_username_input.text().replace(" ", "")
        user_pass = self.user_newpassword_input.text().replace(" ", "")
        user_comfirm_pass = self.user_confirmpassword_input.text().replace(" ", "")

        # Validate and process user input
        if user_pass != user_comfirm_pass:
            # Show a warning message if passwords don't match
            QMessageBox.warning(self, "Unmatched Password", "Please match the password.")
            return
        elif len(user_id) == 0 or len(user_name) == 0 or len(user_position) == 0 or len(user_username) == 0 or len(
                user_pass) == 0:

            # Show an error message if any field is empty
            QMessageBox.critical(self, "Fill all the fields", "Please fill all the fields!")
            return
        else:
            cur = connection.cursor()

            # Check if the user_id or user_username already exists and is active
            cur.execute("SELECT * FROM USER_LOG WHERE (USER_ID = %s OR USER_USERNAME = %s) AND USER_STATUS != 'Inactive'", (user_id, user_username))
            existing_user = cur.fetchone()

            if existing_user is None:
                # Add the new user account
                query = "INSERT INTO USER_LOG (USER_ID, USER_NAME, USER_POSITION, USER_USERNAME, USER_PASSWORD, ADMIN_ID) " \
                        "VALUES (%s, %s, %s, %s, %s, %s)"
                cur.execute(query, (user_id, user_name, user_position, user_username, user_pass, Data.user_id))
                connection.commit()
                cur.close()
                QMessageBox.information(self, "New User Account Added", "New Account Successfully Added")
                self.back_AdminAccounts()
            else:
                # Show a message if the user account already exists
                QMessageBox.information(self, "Admin Account Exists", "Admin account already exists!")
                cur.close()
                return

            # Clear the text in the QLineEdit widgets
            self.user_ID_input.clear()
            self.user_name_input.clear()
            self.user_position_input.clear()
            self.user_username_input.clear()
            self.user_newpassword_input.clear()
            self.user_confirmpassword_input.clear()

    def back_AdminAccounts(self):
        admin_accounts = AdminAccounts()
        widget_stack.addWidget(admin_accounts)
        widget_stack.setCurrentWidget(admin_accounts)


class AdminAccounts_UpdateAdmin(QDialog):
    def __init__(self):
        super(AdminAccounts_UpdateAdmin, self).__init__()
        loadUi("AdminAccs_updateAdmin.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_AdminAccounts)
        self.update_admin_button.clicked.connect(self.update_admin)
        self.admin_ID_input.setValidator(validator_int)

    def update_admin(self):
        admin_id = self.admin_ID_input.text().replace(" ", "")
        admin_name = self.admin_name_input.text().replace(" ", "")
        admin_position = self.admin_position_input.text().replace(" ", "")
        admin_username = self.admin_username_input.text().replace(" ", "")
        admin_pass = self.admin_newpassword_input.text().replace(" ", "")
        admin_comfirm_pass = self.admin_confirmpassword_input.text().replace(" ", "")

        if admin_pass != admin_comfirm_pass:
            QMessageBox.warning(self, "Unmatched Password", "Please match the password.")
            return
        elif len(admin_id) == 0 or len(admin_name) == 0 or len(admin_position) == 0 or len(admin_username) == 0 or len(
                admin_pass) == 0:
            QMessageBox.critical(self, "Fill all the fields", "Please fill all the fields!")
            return
        else:
            cur = connection.cursor()

            # Check if the admin_id already exists
            cur.execute("SELECT * FROM ADMIN_LOG WHERE ADMIN_ID = %s AND ADMIN_STATUS != 'Inactive'", (admin_id,))
            existing_admin = cur.fetchone()

            if existing_admin:
                query = "UPDATE ADMIN_LOG SET ADMIN_NAME = %s, ADMIN_POSITION = %s, ADMIN_USERNAME = %s, ADMIN_PASSWORD = %s" \
                        " WHERE ADMIN_ID = %s AND ADMIN_STATUS != 'Inactive'"
                cur.execute(query, (admin_name, admin_position, admin_username, admin_pass, admin_id))
                connection.commit()
                cur.close()
                QMessageBox.information(self, "Admin Account Updated", "Account Successfully Updated")
                self.back_AdminAccounts()
            else:
                QMessageBox.information(self, "Admin Account not Exists", "Admin account not exists!")
                cur.close()
                return

            # Clear the text in the QLineEdit widgets
            self.admin_ID_input.clear()
            self.admin_name_input.clear()
            self.admin_position_input.clear()
            self.admin_username_input.clear()
            self.admin_newpassword_input.clear()
            self.admin_confirmpassword_input.clear()

    def back_AdminAccounts(self):
        admin_accounts = AdminAccounts()
        widget_stack.addWidget(admin_accounts)
        widget_stack.setCurrentWidget(admin_accounts)


class AdminAccounts_UpdateUser(QDialog):
    def __init__(self):
        super(AdminAccounts_UpdateUser, self).__init__()
        loadUi("AdminAccs_updateUser.ui", self)
        self.adminNamelbl.setText(Data.user_name)
        self.backButton.clicked.connect(self.back_AdminAccounts)
        self.new_admin_button.clicked.connect(self.update_user)
        self.user_ID_input.setValidator(validator_int)

    def update_user(self):
        # Retrieve user input from QLineEdit widgets
        user_id = self.user_ID_input.text()
        user_name = self.user_name_input.text().replace(" ", "")
        user_position = self.user_position_input.text().replace(" ", "")
        user_username = self.user_username_input.text().replace(" ", "")
        user_pass = self.user_newpassword_input.text().replace(" ", "")
        user_comfirm_pass = self.user_confirmpassword_input.text().replace(" ", "")

        # Validate and process user input
        if user_pass != user_comfirm_pass:
            # Show a warning message if passwords don't match
            QMessageBox.warning(self, "Unmatched Password", "Please match the password.")
            return
        elif len(user_id) == 0 or len(user_name) == 0 or len(user_position) == 0 or len(user_username) == 0 or len(
                user_pass) == 0:
            # Show an error message if any field is empty
            QMessageBox.critical(self, "Fill all the fields", "Please fill all the fields!")
            return
        else:
            # Perform the update operation in the database
            cur = connection.cursor()

            # Check if the user_id already exists and is active
            cur.execute("SELECT * FROM USER_LOG WHERE USER_ID = %s AND USER_STATUS != 'Inactive'", (user_id,))
            existing_user = cur.fetchone()

            if existing_user:
                # Update the user account information
                query = "UPDATE USER_LOG SET USER_NAME = %s, USER_POSITION = %s, USER_USERNAME = %s, USER_PASSWORD = %s" \
                        " WHERE USER_ID = %s AND USER_STATUS != 'Inactive'"
                cur.execute(query, (user_name, user_position, user_username, user_pass, user_id))
                connection.commit()
                cur.close()
                QMessageBox.information(self, "Updated user Account", "Account Successfully Updated!")
                self.back_AdminAccounts()
            else:
                # Show a message if the user account does not exist
                QMessageBox.information(self, "Admin Account Not Exists", "Admin account Not exists!")
                cur.close()
                return

            # Clear the text in the QLineEdit widgets
            self.user_ID_input.clear()
            self.user_name_input.clear()
            self.user_position_input.clear()
            self.user_username_input.clear()
            self.user_newpassword_input.clear()
            self.user_confirmpassword_input.clear()

    def back_AdminAccounts(self):
        admin_accounts = AdminAccounts()
        widget_stack.addWidget(admin_accounts)
        widget_stack.setCurrentWidget(admin_accounts)


class Admin_BackupandRecovery(QDialog):
    def __init__(self):
        super(Admin_BackupandRecovery, self).__init__()
        loadUi("Admin_BackupandRecovery.ui", self)

        # Set the admin name label
        self.adminNamelbl.setText(Data.user_name)

        # Connect button signals to their respective slots
        self.button_backup_database.clicked.connect(self.backup_database)
        self.button_restore_database.clicked.connect(self.restore_database)
        self.backButton.clicked.connect(self.back_admin)

    def backup_database(self):
        # Database name to backup
        db_name = 'sunvoltage_system'

        # Open file dialog to choose the backup file location
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setDefaultSuffix('.sql')
        file_dialog.exec()

        # Get the selected file path
        file_paths = file_dialog.selectedFiles()
        if file_paths:
            backup_file = file_paths[0]
            self.execute_pg_dump(db_name, backup_file)

    def restore_database(self):
        # Database name to restore
        db_name = 'sunvoltage_system'

        # Open file dialog to choose the restore file
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.exec()

        # Get the selected file path
        file_paths = file_dialog.selectedFiles()
        if file_paths:
            restore_file = file_paths[0]
            self.execute_psql(db_name, restore_file)

    def execute_pg_dump(self, db_name, output_file):
        host = '127.0.0.1'
        port = '5432'
        user = 'postgres'
        password = '200303'

        try:
            # Execute the pg_dump command to backup the database
            subprocess.run(['pg_dump', f'--dbname=postgresql://{user}:{password}@{host}:{port}/{db_name}',
                            '--file=' + output_file], check=True)
            QMessageBox.information(self, "Database Backup Succesfully", "The database is backup successfully")
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Backup Failed", f"The database backup failed: {e}")

    def execute_psql(self, db_name, input_file):
        host = '127.0.0.1'
        port = '5432'
        user = 'postgres'
        password = '200303'

        try:
            # Execute the psql command to restore the database
            subprocess.run(['psql', f'--dbname=postgresql://{user}:{password}@{host}:{port}/{db_name}',
                            '--file=' + input_file], check=True)
            QMessageBox.information(self, "Database Restored Succesfully", "The database is restored successfully")
            connection.close()
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Restore Failed", f"The database restore failed: {e}")
    def back_admin(self):
        # Navigate back to the admin dashboard
        admin_dashboard = AdminDashboardWindow()
        widget_stack.addWidget(admin_dashboard)
        widget_stack.setCurrentWidget(admin_dashboard)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget_stack = QStackedWidget()

    # Create instances of various windows or views
    login_window = LoginWindow()
    admin_dashboard_window = AdminDashboardWindow()
    user_dashboard_window = UserDashboardWindow()
    user_inventory_materials = Inventory_Material_User()
    user_inventory_equipments = Inventory_Equipment_User()
    user_project = Project_User()
    user_report = User_Report()
    user_employee_list = User_EmployeeList()
    admin_employee = Admin_EmployeeList()
    employee_add = Add_Employee()
    employee_payroll = Employee_Payroll()
    admin_inventory_material = Inventory_Material_Admin()
    admin_inventory_addmaterial = Inventory_AddMaterial_Admin()
    admin_inventory_equipment = Inventory_Equipment_Admin()
    admin_inventory_addequipment = Inventory_AddEquipment_Admin()
    admin_project = Admin_Project()
    admin_new_project = Admin_Add_Project()
    admin_ongoings_project = Admin_Ongoings_Project()
    admin_accomplish_project = Admin_Accomplished_Project()
    admin_assign_project = Admin_Assign_Employee_Proj()
    admin_accounts = AdminAccounts()
    admin_accounts_new_admin = AdminAccounts_NewAdmin()
    admin_accounts_new_user = AdminAccounts_NewUser()
    admin_account_update_admin = AdminAccounts_UpdateAdmin()
    admin_account_update_user = AdminAccounts_UpdateUser()
    admin_backuprecover = Admin_BackupandRecovery()

    # Add the windows or views to the widget stack
    widget_stack.addWidget(login_window)
    widget_stack.addWidget(admin_dashboard_window)
    widget_stack.addWidget(user_dashboard_window)
    widget_stack.addWidget(user_inventory_materials)
    widget_stack.addWidget(admin_inventory_addmaterial)
    widget_stack.addWidget(user_inventory_equipments)
    widget_stack.addWidget(admin_inventory_addequipment)
    widget_stack.addWidget(user_project)
    widget_stack.addWidget(user_report)
    widget_stack.addWidget(user_employee_list)
    widget_stack.addWidget(admin_employee)
    widget_stack.addWidget(employee_add)
    widget_stack.addWidget(employee_payroll)
    widget_stack.addWidget(admin_inventory_material)
    widget_stack.addWidget(admin_inventory_equipment)
    widget_stack.addWidget(admin_project)
    widget_stack.addWidget(admin_new_project)
    widget_stack.addWidget(admin_ongoings_project)
    widget_stack.addWidget(admin_accomplish_project)
    widget_stack.addWidget(admin_assign_project)
    widget_stack.addWidget(admin_accounts)
    widget_stack.addWidget(admin_accounts_new_admin)
    widget_stack.addWidget(admin_accounts_new_user)
    widget_stack.addWidget(admin_account_update_admin)
    widget_stack.addWidget(admin_account_update_user)
    widget_stack.addWidget(admin_backuprecover)

    # Set the fixed size and show the widget stack
    widget_stack.setFixedSize(900, 500)
    widget_stack.show()

    sys.exit(app.exec())
