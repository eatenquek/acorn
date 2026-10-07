from pathlib import Path
from html import escape
import textwrap
ROOT=Path(__file__).parent
OUT=ROOT/'figma-screens';OUT.mkdir(exist_ok=True)
cream='#faf6ed';brown='#402c22';muted='#74685b';green='#45634b';line='#e3dacb'
def rect(x,y,w,h,fill,rx=0,stroke='none'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'
def text(x,y,s,size=14,color=brown,font='Plus Jakarta Sans',weight=400):
 return f'<text x="{x}" y="{y}" font-family="{font}, Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(s)}</text>'
def para(x,y,s,width=40,size=14,color=muted):
 return ''.join(text(x,y+i*22,row,size,color) for i,row in enumerate(textwrap.wrap(s,width)))
def button(y,s,secondary=False):
 return rect(24,y,342,52,cream if secondary else brown,13,line if secondary else 'none')+text(42,y+32,s,14,brown if secondary else cream,weight=600)
def forest(y,rest=False,bench=False):
 s=rect(0,y,390,260,'#e8ede0')+f'<circle cx="312" cy="{y+43}" r="23" fill="#ecd8ae"/>'+f'<path d="M0 {y+170}q100-95 210-30t180-22v142H0" fill="#a4b791"/>'+f'<path d="M0 {y+230}q90-60 195-15t195-17v62H0" fill="#bec297"/>'
 for x,ty,scale,c in [(35,181,.75,'#8ea17a'),(320,175,.85,'#7b9973'),(183,230,1.5,'#516e4c'),(71,225,.5,'#6d865c'),(352,235,.5,'#5e7d54')]:
  s+=f'<g transform="translate({x} {y+ty}) scale({scale})"><path d="M-4 0V-90h8V0" fill="#775e44"/><path d="m0-116-33 53h17l-27 41h26L-35 0h70L17-22h26L16-63h17z" fill="{c}"/></g>'
 s+=f'<g transform="translate(259 {y+222})"><path d="M0 0c25-2 29-38 8-38-21 0-20 18-8 22 6 2 8-7 2-8 15 0 9 17-3 14" fill="#ad7544"/><ellipse cx="-5" cy="-4" rx="13" ry="10" fill="#b9804e"/><circle cx="-15" cy="-14" r="9" fill="#bb8957"/><path d="m-20-20 2-10 5 11m2 0 5-9 2 12" fill="#a16b42"/><ellipse cx="-19" cy="-10" rx="6" ry="4" fill="#debe90"/>'
 s+=('<path d="m-19-15 5 1" stroke="#402c22"/>' if rest else '<circle cx="-18" cy="-16" r="1.5" fill="#402c22"/>')+'</g>'
 if bench:s+=f'<path d="M50 {y+208}h38m-38 8h38m-41 9h44m-36 0v14m28-14v14" fill="none" stroke="#775e44" stroke-width="4"/>'
 return s
screens=[
('01-forest','Your forest.','A little care, taking root.','home'),
('02-add','Start with your','prescription.','add'),
('03-scan','A photo.','A simpler start.','scan'),
('04-review','Does this match?','A draft for you to check.','review'),
('05-time','A time to remember.','Explicit time from the prescription.','time'),
('06-saved','A little less','to remember.','saved'),
('07-log','How did it go?','Record what happened.','log'),
('08-rest','A quieter moment.','This dose is recorded as missed.','rest'),
('09-hold','Let’s not guess.','Nothing has been scheduled.','hold'),
('10-pdf','Bring your','medication PDF.','pdf'),
('11-reminder','Choose a reminder.','Your preference, clearly labeled.','reminder'),
('12-clearing','Make yourself','at home.','clearing')]
frames=[]
for index,(name,title,subtitle,kind) in enumerate(screens):
 s=rect(0,0,390,844,cream,28)+text(26,29,'9:41',11,weight=600)+rect(150,9,90,22,brown,13)+text(26,77,'‹',24)+text(302,77,'acorn',18,font='Fraunces')+text(24,126,'A LITTLE CARE, EVERY DAY',10,green,weight=600)
 s+=text(24,171,title,31,font='Fraunces')+text(24,204,subtitle,15,muted)
 if kind=='home':
  s+=forest(231)+text(24,526,'7 growth days · demonstration',12,green)+text(24,574,'Today’s care',25,font='Fraunces')+rect(24,597,342,124,'#fffcf5',15,line)+text(40,625,'08:00 · NOT RECORDED',10,muted)+text(40,653,'Example medicine 10 mg tablets',14,weight=600)+text(40,680,'One tablet · by mouth',13,muted)+button(739,'Record dose')
 elif kind=='add':
  for y,a,b in [(265,'Scan a prescription label','Quickest to try · one medicine at a time'),(392,'Import a medication PDF','Use a reference record you exported'),(519,'Enter the details yourself','Keep your current prescription nearby')]:
   s+=rect(24,y,342,104,'#f1f2e6' if y==265 else '#fffcf5',15,line)+text(42,y+36,a,16,weight=600)+text(42,y+68,b,12,muted)
  s+=para(24,682,'You will review everything before it becomes a schedule.',42,13)
 elif kind=='scan':
  s+=para(24,245,'Include the name, strength and full directions.',41)+rect(24,303,342,233,'#e8eadd',18)+rect(48,348,294,142,'white',4)+text(62,375,'SYNTHETIC DEMO LABEL',10,muted)+text(62,407,'Example medicine 10 mg tablets',14,weight=600)+text(62,435,'Take ONE tablet by mouth',13)+text(62,458,'at 08:00 every day.',13)+para(24,590,'Keep the label flat and well lit. All extracted details need your review.',40)+button(701,'Choose a label photo')+button(765,'Try the sample label',True)
 elif kind=='review':
  s+=rect(24,236,342,102,'#fffcf5',14,line)+text(40,262,'DIRECTIONS READ FROM LABEL',10,muted)+text(40,290,'Take ONE tablet by mouth',14)+text(40,315,'at 08:00 every day.',14)
  for y,label,value in [(365,'Medicine','Example medicine 10 mg tablets'),(457,'Strength','10 mg'),(549,'Amount per dose','one tablet')]:s+=text(24,y,label,12,weight=600)+rect(24,y+12,342,48,'#fffcf5',10,line)+text(38,y+42,value,14)
  s+=para(24,674,'I checked these details against my current prescription.',42,12)+button(765,'Continue to schedule')
 elif kind in ['time','reminder']:
  s+=para(24,246,'This is written in your directions.' if kind=='time' else 'No clock time was written. Choose when you want a reminder.',40)+rect(24,316,342,113,'#fffcf5',14,line)+text(40,346,'CURRENT DIRECTIONS',10,muted)+para(40,376,'Take ONE tablet by mouth '+('at 08:00 every day.' if kind=='time' else 'once daily.'),35,14,brown)+text(24,475,'Time from prescription' if kind=='time' else 'Your reminder preference',12,weight=600)+rect(24,490,342,64,'#fffcf5',11,line)+text(42,530,'08:00' if kind=='time' else '— — : — —',25,font='Fraunces')+para(24,590,'Confirm that this matches your current prescription before saving.',42)+para(24,679,'Prototype only: device notifications are not enabled.',45,12)+button(765,'Confirm my schedule')
 elif kind=='saved':
  s+=text(24,262,'SCHEDULE SAVED',12,green,weight=600)+rect(24,293,342,111,'#e7eddf',14)+text(42,325,'08:00 · EVERY DAY',12,green)+text(42,357,'Example medicine 10 mg tablets',14,weight=600)+text(42,384,'One tablet · by mouth',13,muted)+forest(433)+button(765,'Back to my forest')
 elif kind=='log':
  s+=rect(24,265,342,160,'#fffcf5',14,line)+text(42,299,'08:00 · SYNTHETIC DEMO',11,muted)+text(42,337,'Example medicine 10 mg tablets',14,weight=600)+text(42,375,'One tablet · by mouth',14)+para(24,481,'This records a dose. Follow your prescription for how and when to take it.',40)+button(630,'I took this dose')+button(696,'I missed this dose',True)+text(62,804,'Leave it unrecorded for now',13,muted)
 elif kind=='rest':
  s+=forest(236,True)+text(24,540,'Everything you’ve grown',25,font='Fraunces')+text(24,572,'is still here.',25,font='Fraunces')+para(24,614,'For advice about a missed dose, check your medicine’s instructions or ask your pharmacist or care team.',42,13)+button(727,'Return to my forest')+text(125,813,'Correct this log',12,muted)
 elif kind=='hold':
  s+=rect(24,263,342,109,'#fffcf5',14,line)+text(40,292,'DIRECTIONS FOUND',10,muted)+para(40,324,'Take ONE tablet by mouth as needed.',33,15,brown)+rect(24,416,342,152,'#f6ecd5',14)+para(40,451,'These directions do not become a repeating schedule. Check the exact dose and timing with your pharmacist or care team.',35,14,'#6a481d')+para(24,620,'Your Forest is unchanged. Nothing has been scheduled.',42)+button(701,'Try a clearer label')+button(765,'Back to my forest',True)
 elif kind=='pdf':
  for y,a,b in [(280,'01  Open HealthHub','Services → Medications → Prescription records'),(390,'02  Download the PDF','View details → download for your reference'),(500,'03  Import and check','Confirm which directions are still current')]:s+=text(24,y,a,17,weight=600)+para(24,y+30,b,43,12)
  s+=rect(24,596,342,92,'#f6ecd5',13)+para(40,625,'Reference records may be incomplete or out of date. Confirm against your current prescription.',38,12,'#6a481d')+button(765,'Choose medication PDF')
 elif kind=='clearing':
  s+=forest(239,bench=True)+text(24,541,'12 acorns · only for cosmetics',12,green)+rect(24,575,342,119,'#fffcf5',14,line)+text(42,610,'A quiet bench',21,font='Fraunces')+text(42,642,'8 acorns · yours to keep',13,muted)+para(24,727,'Decorations never add adherence days or change your medication record.',43,13)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="390" height="844" viewBox="0 0 390 844">{s}</svg>'
 (OUT/f'{name}.svg').write_text(svg)
 x=40+(index%4)*430;y=160+(index//4)*920
 frames.append(f'<g transform="translate({x} {y})">{text(0,-17,name.upper(),12,muted,weight=600)}{s}</g>')
board=f'<svg xmlns="http://www.w3.org/2000/svg" width="1760" height="2925" viewBox="0 0 1760 2925">{rect(0,0,1760,2925,"#eae5da")}{text(40,62,"acorn — a routine, taking root.",38,font="Fraunces")}{text(40,104,"Prescription → review → schedule → care. Editable vector storyboard; interaction spec in FIGMA-HANDOFF.md.",16,muted)}'+''.join(frames)+'</svg>'
(ROOT/'storyboard.svg').write_text(board)
print('Created 12 editable SVG screens and storyboard.svg')
