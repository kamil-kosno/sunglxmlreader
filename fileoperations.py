import os

import pandas
import csv
from lxml import etree
from flask import session
import shutil
from datetime import datetime

USER_FILES = "./userfiles/"
HEADER_FILE = "sun_gl_response_header.csv"
HEADER_FIELDS = ["BusinessUnit", "BudgetCode", "AllowBalTran", "AllowPostToSuspended", "LoadOnly", "PostProvisional",
                 "PostToHold", "PostingType", "ReportErrorsOnly", "ReportingAccount", "SuppressSubstitutedMessages",
                 "SuspenseAccount", "TransactionAmountAccount"]
PAYLOAD_FILE = "sun_gl_response_payload.csv"
PAYLOAD_FIELDS = ["RowNumber", "AccountCode", "AccountingPeriod", "AnalysisCode1", "AnalysisCode2", "AnalysisCode6",
                  "CurrencyCode", "DebitCredit", "Description", "JournalType", "TransactionAmount", "TransactionDate",
                  "TransactionReference", "GeneralDescription5", "GeneralDescription6", "TopErrorMessage"]
COMBINED_FILE = "sun_gl_response_failed_records.csv"
LOG_FILE = 'user_active.log'

class FileOperations:
    def __init__(self, user_session_id):
        self.user_session_id = user_session_id

    def get_root(self):
        root = f"{USER_FILES}{self.user_session_id}/"
        if not os.path.exists(root):
            os.makedirs(root)
        return root

    def get_file_path(self, filename):
        return f"{self.get_root()}{filename}"

    def get_log_file_path(self):
        return self.get_file_path(LOG_FILE)

    def get_header_file_path(self):
        return self.get_file_path(HEADER_FILE)

    def get_payload_file_path(self):
        return self.get_file_path(PAYLOAD_FILE)

    def get_combined_file_path(self):
        return self.get_file_path(COMBINED_FILE)

    def clean_temp_folder(self):
        # clean up user directory
        try:
            for f in os.scandir(USER_FILES):
                if f.is_file():
                    os.remove(f.path)
                else:
                    if f.name == self.user_session_id:
                        shutil.rmtree(f.path)
                    else:
                        last_modified_time = datetime.fromtimestamp(f.stat().st_mtime)
                        for file in os.scandir(f.path):
                            last_modified = datetime.fromtimestamp(file.stat().st_mtime)
                            if last_modified > last_modified_time:
                                last_modified_time = last_modified                        
                        now_time = datetime.now()
                        if (now_time-last_modified_time).total_seconds() > 300:
                            shutil.rmtree(f.path)
        except Exception as e:
            return f"Failed to clean up file folder. Reason: {e}"

    def parse_xml(self, file_name):
        with open(file_name, "r") as f:
            raw = f.read()
            # save header details as csv (e.g. business unit, budget code etc.)
            xml = etree.fromstring(raw[raw.find('<SSC>'):])
            business_unit = xml.find('SunSystemsContext/BusinessUnit')
            budget_code = xml.find('SunSystemsContext/BudgetCode')
            allow_bal_tran = xml.find('MethodContext/LedgerPostingParameters/AllowBalTran')
            allow_post_to_suspended = xml.find('MethodContext/LedgerPostingParameters/AllowPostToSuspended')
            load_only = xml.find('MethodContext/LedgerPostingParameters/LoadOnly')
            post_provisional = xml.find('MethodContext/LedgerPostingParameters/PostProvisional')
            post_to_hold = xml.find('MethodContext/LedgerPostingParameters/PostToHold')
            posting_type = xml.find('MethodContext/LedgerPostingParameters/PostingType')
            report_errors_only = xml.find('MethodContext/LedgerPostingParameters/ReportErrorsOnly')
            reporting_account = xml.find('MethodContext/LedgerPostingParameters/ReportingAccount')
            suppress_substituted_messages = xml.find('MethodContext/LedgerPostingParameters/SuppressSubstitutedMessages')
            suspense_account = xml.find('MethodContext/LedgerPostingParameters/SuspenseAccount')
            transaction_amount_account = xml.find('MethodContext/LedgerPostingParameters/TransactionAmountAccount')
            with open(self.get_header_file_path(), "w", newline='') as hf:
                csvw = csv.writer(hf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csvw.writerow(HEADER_FIELDS)
                csvw.writerow([
                    business_unit.text if business_unit is not None else '',
                    budget_code.text if budget_code is not None else '',
                    allow_bal_tran.text if allow_bal_tran is not None else '',
                    allow_post_to_suspended.text if allow_post_to_suspended is not None else '',
                    load_only.text if load_only is not None else '',
                    post_provisional.text if post_provisional is not None else '',
                    post_to_hold.text if post_to_hold is not None else '',
                    posting_type.text if posting_type is not None else '',
                    report_errors_only.text if report_errors_only is not None else '',
                    reporting_account.text if reporting_account is not None else '',
                    suppress_substituted_messages.text if suppress_substituted_messages is not None else '',
                    suspense_account.text if suspense_account is not None else '',
                    transaction_amount_account.text if transaction_amount_account is not None else ''
                ])
            # save ledger line details
            with open(self.get_payload_file_path(), "w", newline='') as pf:
                csvw = csv.writer(pf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csvw.writerow(PAYLOAD_FIELDS)
                row_num = 1
                for node in xml.findall('Payload/Ledger/Line[@status="fail"]'):
                    account_code = node.find('AccountCode')
                    accounting_period = node.find('AccountingPeriod')
                    analysis_code_1 = node.find('AnalysisCode1')
                    analysis_code_2 = node.find('AnalysisCode2')
                    analysis_code_6 = node.find('AnalysisCode6')
                    currency_code = node.find('CurrencyCode')
                    debit_credit = node.find('DebitCredit')
                    description = node.find('Description')
                    journal_type = node.find('JournalType')
                    transaction_amount = node.find('TransactionAmount')
                    transaction_date = node.find('TransactionDate')
                    transaction_reference = node.find('TransactionReference')
                    general_description_5 = node.find('DetailLad/GeneralDescription5')
                    general_description_6 = node.find('DetailLad/GeneralDescription6')
                    top_error_message = node.find('Messages/Message[@Level="error"]/UserText')
                    csvw.writerow([
                        row_num,
                        account_code.text if account_code is not None else '',
                        accounting_period.text if accounting_period is not None else '',
                        analysis_code_1.text if analysis_code_1 is not None else '',
                        analysis_code_2.text if analysis_code_2 is not None else '',
                        analysis_code_6.text if analysis_code_6 is not None else '',
                        currency_code.text if currency_code is not None else '',
                        debit_credit.text if debit_credit is not None else '',
                        description.text if description is not None else '',
                        journal_type.text if journal_type is not None else '',
                        transaction_amount.text if transaction_amount is not None else '',
                        transaction_date.text if transaction_date is not None else '',
                        transaction_reference.text if transaction_reference is not None else '',
                        general_description_5.text if general_description_5 is not None else '',
                        general_description_6.text if general_description_6 is not None else '',
                        top_error_message.text.strip() if top_error_message is not None else ''
                    ])
                    row_num+=1
        with open(self.get_combined_file_path(), 'w', newline='') as fwrite:
            csvw = csv.writer(fwrite, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            with open(self.get_header_file_path(), 'r') as fread_header:
                csvr = csv.reader(fread_header, delimiter=',', quotechar='"')
                for row in csvr:
                    if csvr.line_num == 1:
                        columns = row
                    else:
                        for i in range(len(columns)):
                            csvw.writerow([columns[i], row[i]])
            csvw.writerow([])
            with open(self.get_payload_file_path(), 'r') as fread_payload:
                fwrite.write(fread_payload.read())
        return True
    
    def write_log(self):
        with open(self.get_log_file_path(), 'w') as log_writer:
            log_writer.write(f"last active: {datetime.now()}")
        return True

    def get_header(self):
        return pandas.read_csv(self.get_header_file_path(), keep_default_na=False, dtype=str)

    def get_payload(self):
        return pandas.read_csv(self.get_payload_file_path(), keep_default_na=False, dtype=str)
