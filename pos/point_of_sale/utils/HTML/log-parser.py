# import HTML
from pos.point_of_sale.utils.HTML import HTML
# open an HTML file to show output in a browser
import re
import traceback





log_file_path = r"C:\html\mini\PrepaidCard.OneClickShortPage - Updated.txt"
HTMLFILE = 'C:\html\mini\PrepaidCard.OneClickShortPage - Updated.html'
# log_file_path = r"C:\test_cases\ParsedLog.txt"
log_file = open(log_file_path, 'r', encoding='utf-8')

d = []
cnt_scenario = 1
cnt_prep_data = 1
cnt_steps = 1
cnt_asserts = 1
cnt_quick_summary = 1

test_name = ""
lines = log_file.readlines()
current_testcase = ''
prep_data = ''

summary = ''
tmp_list = []

for line in lines:
    if not re.match(r'^\s*$', line):
        if '---' in line:
            tmp_list = []
            group = ["GroupX:", {line}]
            tmp_list.append(group)
            if not tmp_list == []:
                d.append(tmp_list)
                
            # if '---' in line:
            #     if not tmp_list == []:
            #         d.append(tmp_list)
            #         tmp_list = []

                current_testcase = [f"Test_Case_{cnt_scenario}", line]
        elif 'Master ' in line:
            # if not tmp_list == []:
            #     d.append(tmp_list)
            #     tmp_list = []
            
            current_testcase = [f"Test_Case_{cnt_scenario}", line]
            cnt_prep_data = 1
            cnt_steps = 1
            cnt_scenario += 1
            cnt_asserts = 1
            tmp_list.append(current_testcase)
            tmp = line.split('PointOfSale.')
            try:
                summary = [f"Summary: {cnt_quick_summary}", tmp[1]]
                tmp_list.append(summary)
                cnt_quick_summary += 1
            except Exception as ex:
                traceback.print_exc()
                pass
        
        elif 'Debug Information' in line or '-- Initialization --' in line or 'AssertAdditionalInfo' in line:
            z = 'donothing'
        
        elif '\t\t\t' in line:
            tmp_cleanstr = line.replace('\t\t\t', '')
            summary = [f"Summary :", {tmp_cleanstr}]
            tmp_list.append(summary)
            cnt_quick_summary += 1
        
        elif 'Preparing Data' in line:
            tmp = line.split('Data] ')
            prep_data = [f"Data Preparation Step:{cnt_prep_data}", tmp[1]]
            tmp_list.append(prep_data)
            cnt_prep_data += 1
        
        elif 'PayPage Action' in line:
            tmp = line.split(']')
            steps = [f"Test_Step:{cnt_steps} - (PayPage)", tmp[1]]
            tmp_list.append(steps)
            cnt_steps += 1
        
        elif 'JobManager' in line:
            tmp = line.split(']')
            steps = [f"Test_Step:{cnt_steps} - (JobManager)", tmp[1]]
            tmp_list.append(steps)
            cnt_steps += 1
        
        elif 'Assert' in line:
            tmp = line.split(']')
            tmp_cleanstr = tmp[0].replace('[', '')
            if 'Assert' in tmp[0]:
                asserts = [f"Verifications:", tmp[1]]
                cnt_asserts = 1
                tmp_list.append(asserts)
        
        elif '\t' in line:  # asserts
            tmp_cleanstr = line.replace('\t', '')
            asserts = [f"Assert Check: {cnt_asserts} ", tmp_cleanstr]
            cnt_asserts += 1
            tmp_list.append(asserts)
# writing HTML
#HTMLFILE = 'C:\html\mini\mCard_BccEu_PayvisionUs_Signup_Capture_Rebill_Refund.html'
f = open(HTMLFILE, 'w', encoding='utf-8')

for tc in d:
    try:
        t = HTML.Table(header_row=[HTML.TableCell('Test Case', bgcolor='green'), 'Details', 'Comments'],
                       col_align=['left', 'char', 'right'],
                       col_styles=['font-size: small', 'font-size: small', 'font-size: small'],
                       # col_width=['', '', '']
                       )
        
        t.rows.append([HTML.TableCell('', bgcolor='LightGoldenRodYellow'), HTML.TableCell("", bgcolor='LightGoldenRodYellow'),
                       HTML.TableCell('', bgcolor='LightGoldenRodYellow')])
        t.rows.append([HTML.TableCell('', bgcolor='LightGoldenRodYellow'), HTML.TableCell("", bgcolor='LightGoldenRodYellow'),
                       HTML.TableCell('', bgcolor='LightGoldenRodYellow')])
        for testcase in tc:
            if 'GroupX' in testcase[0]:
                t.rows.append([HTML.TableCell('Test Case Name', bgcolor='LightGoldenRodYellow'), HTML.TableCell(testcase[1], bgcolor='LightGoldenRodYellow'),
                               HTML.TableCell('Test Case Name', bgcolor='LightGoldenRodYellow')])
            
            if 'Data Preparation Step:1' in testcase:
                t.rows.append([HTML.TableCell('', bgcolor='LightGoldenRodYellow'), HTML.TableCell('Prerequisites', bgcolor='LightGoldenRodYellow'),
                               HTML.TableCell('Prerequisites', bgcolor='LightGoldenRodYellow')])
            elif 'Test_Step:1 -' in testcase[0]:
                t.rows.append([HTML.TableCell('', bgcolor='LightGoldenRodYellow'), HTML.TableCell('Test Steps', bgcolor='LightGoldenRodYellow'),
                               HTML.TableCell('Test Steps', bgcolor='LightGoldenRodYellow')])
            elif 'Summary: 1' in testcase[0]:
                t.rows.append([HTML.TableCell('', bgcolor='LightGoldenRodYellow'), HTML.TableCell('Test Case Summary', bgcolor='LightGoldenRodYellow'),
                               HTML.TableCell('Test Case Summary', bgcolor='LightGoldenRodYellow')])
            elif "Verifications" in testcase[0]:
                t.rows.append([HTML.TableCell('', bgcolor='LightGoldenRodYellow'), HTML.TableCell(f"Verifications Steps - {testcase[1]}", bgcolor='LightGoldenRodYellow'),
                               HTML.TableCell('Verifications Steps', bgcolor='LightGoldenRodYellow')])
            
            if 'Summary' in testcase[0]:
                t.rows.append([HTML.TableCell('Test Case Info', bgcolor='LightGray'), HTML.TableCell(testcase[1], bgcolor='LightGray'), ''])
                # print(testcase[1])
            
            if 'Data Preparation Step' in testcase[0]:
                t.rows.append([HTML.TableCell(testcase[0], bgcolor='LightGray'), HTML.TableCell(testcase[1], bgcolor='LightGray'), ''])
            elif 'Test_Step:' in testcase[0]:
                t.rows.append([HTML.TableCell(testcase[0], bgcolor='Beige'), HTML.TableCell(testcase[1], bgcolor='Beige'), ''])  # Bisque
            elif 'Assert' in testcase[0]:
                t.rows.append([HTML.TableCell(testcase[0], bgcolor='HoneyDew'), HTML.TableCell(testcase[1], bgcolor='HoneyDew'), ''])
            # else:
            #     t.rows.append([testcase[0], testcase[1], ''])
        
        htmlcode = str(t)
        # print(htmlcode)
        f.write(htmlcode)
        f.write('<p>')
        f.write('<p>')
        # print('-' * 79)
    except Exception as ex:
        traceback.print_exc()
        print()
f.close()
