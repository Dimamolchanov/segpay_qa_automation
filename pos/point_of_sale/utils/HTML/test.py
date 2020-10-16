#import HTML
from pos.point_of_sale.utils.HTML import HTML
# open an HTML file to show output in a browser
import re

log_file_path = r"C:\html\ParsedLog.txt"
#log_file_path = r"C:\test_cases\ParsedLog.txt"
log_file = open(log_file_path, 'r')

d = []
cnt_scenario = 1
cnt_prep_data = 1
cnt_steps = 1
cnt_asserts = 1
test_name = ""
lines = log_file.readlines()
current_testcase = ''
prep_data = ''
tmp_list = []
for line in lines:
    if not re.match(r'^\s*$', line):
        if '---' in line:
            if not tmp_list == []:
                d.append(tmp_list)
                tmp_list = []
            
            current_testcase = [f"Test_Case_{cnt_scenario}", line]
            cnt_prep_data = 1
            cnt_steps = 1
            cnt_scenario += 1
            cnt_asserts = 1
            tmp_list.append(current_testcase)
        elif 'Preparing Data' in line:
            tmp = line.split(']')
            prep_data = [f"Data Preparation Step:{cnt_prep_data}", tmp[1]]
            tmp_list.append(prep_data)
            cnt_prep_data += 1
        else:
            tmp = line.split(']')
            tmp_cleanstr = tmp[0].replace('[', '')
            if 'Assert' in tmp[0]:
                asserts = [f"Assert: {cnt_asserts} ", tmp[1]]
                cnt_asserts += 1
                tmp_list.append(asserts)
                
            else:
                steps = [f"Test_Step: {cnt_steps} : ({tmp_cleanstr}) ", tmp[1]]
                tmp_list.append(steps)
                cnt_steps += 1

HTMLFILE = 'HTML_tutorial_output.html'
f = open(HTMLFILE, 'w')

for tc in d:
    t = HTML.Table(header_row=['Test Case', 'Details', 'Comments'], col_align=['left', 'char', 'right'])
    
    for testcase in tc:
        if 'Data Preparation Step:1' in testcase:
            t.rows.append([HTML.TableCell('Prerequisites', bgcolor='LightGoldenRodYellow'), HTML.TableCell('', bgcolor='LightGoldenRodYellow'),
                           HTML.TableCell('Prerequisites', bgcolor='LightGoldenRodYellow')])
        elif 'Test_Step: 1 :' in testcase[0]:
            t.rows.append([HTML.TableCell('Test Steps', bgcolor='LightGoldenRodYellow'), HTML.TableCell('', bgcolor='LightGoldenRodYellow'),
                           HTML.TableCell('Test Steps', bgcolor='LightGoldenRodYellow')])
        
        
        elif testcase[0] == 'Assert: 1 ':
            t.rows.append([HTML.TableCell('Verifications Steps', bgcolor='LightGoldenRodYellow'), HTML.TableCell('', bgcolor='LightGoldenRodYellow'),
                           HTML.TableCell('Verifications Steps', bgcolor='LightGoldenRodYellow')])
        
        if 'Data Preparation Step' in testcase[0]:
            t.rows.append([HTML.TableCell(testcase[0], bgcolor='LightGray'), HTML.TableCell(testcase[1], bgcolor='LightGray'), ''])
        elif 'Test_Step:' in testcase[0]:
            t.rows.append([HTML.TableCell(testcase[0], bgcolor='Beige'), HTML.TableCell(testcase[1], bgcolor='Beige'), ''])  # Bisque
        elif 'Assert:' in testcase[0]:
            t.rows.append([HTML.TableCell(testcase[0], bgcolor='BurlyWood'), HTML.TableCell(testcase[1], bgcolor='BurlyWood'), ''])
        else:
            t.rows.append([testcase[0], testcase[1], ''])
    
    htmlcode = str(t)
    print(htmlcode)
    f.write(htmlcode)
    f.write('<p>')
    f.write('<p>')
    print('-' * 79)

f.close()
