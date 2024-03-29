# Import necessary modules
from distutils.command.build_scripts import first_line_re
from urllib import response
import requests
import csv
import os
from datetime import datetime, timedelta
import pandas as pd
from matplotlib import pyplot as plt
import boto3



# Get Rapid API key from environment variables
RAPID_API_KEY = os.getenv('RAPID_API_KEY')

# Get the current date in the format 'YYYY-MM-DD'
today_date = datetime.today().strftime('%Y-%m-%d')


ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')


# totReb, assists




# Function to make a request to the NBA API for a specific player and season
def hit_nba_api(player_id, season):
    """
    Make a request to the NBA API to retrieve player statistics for a specific player and season.

    Parameters:
    - player_id (int): The unique identifier for the NBA player.
    - season (int): The season for which the statistics are requested.

    Returns:
    - PLAYER_DATA_RESPONSE (dict): Response containing player statistics.
    - player_id (int): Player identifier.
    - season (int): Season identifier.
    """
    # API endpoint URL
    url = "https://api-nba-v1.p.rapidapi.com/players/statistics"

    # Query parameters for the API request
    querystring = {"id": f"{player_id}", "season": f"{season}"}

    # Headers for the API request
    headers = {
        "X-RapidAPI-Key": f"{RAPID_API_KEY}",
        "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com"
    }

    # Make a GET request to the API
    response = requests.get(url, headers=headers, params=querystring)

    # Print the JSON response from the API
    print('\n\n', response.json())

    # Extract player data from the JSON response
    PLAYER_DATA = response.json()
    PLAYER_DATA_RESPONSE = PLAYER_DATA['response']

    return PLAYER_DATA_RESPONSE, player_id, season


# Function to write player data to a CSV file
def write_player_data_csv(PLAYER_DATA_RESPONSE, player_id, season):
    """
    Write player data to a CSV file.

    Parameters:
    - PLAYER_DATA_RESPONSE (dict): Response containing player statistics.
    - player_id (int): Player identifier.
    - season (int): Season identifier.

    Returns:
    - player_id (int): Player identifier.
    - season (int): Season identifier.
    """
    # Initialize an empty list to store data
    stack = []



    # Extract relevant data from the API response and append to the list
    for x in PLAYER_DATA_RESPONSE:
        game_id = x['game']['id']
        points = x['points']
        rebounds = x['totReb']
        assists = x['assists']

        stack.append([game_id, points, rebounds, assists])

    team_logo = PLAYER_DATA_RESPONSE[0]['team']['logo']
    player_full_name = PLAYER_DATA_RESPONSE[0]['player']['firstname'] + ' ' + PLAYER_DATA_RESPONSE[0]['player']['lastname']

    # Print the extracted data
    print(stack)

    # Sort the data based on the game ID
    sort_stack = sorted(stack, key=lambda x: x[0])

    # Create and write to a CSV file
    with open(f'baller_files/gamepoints_{player_id}_{season}_{today_date}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Row', 'Game', 'Points', 'Rebounds', 'Assists'])
        increment = 1
        for x in sort_stack:
            x.insert(0, increment)
            writer.writerow(x)
            increment = increment + 1

    return player_id, season, player_full_name, team_logo


# Function to draw a graph based on player data


def draw_graph(player_id, season):
    """
    Draw a graph based on player data and save it as an image.

    Parameters:
    - player_id (int): Player identifier.
    - season (int): Season identifier.
    """
    # Set up plot configurations
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    plt.rcParams["figure.autolayout"] = True
    plt.title("Player Stats")

    # Specify columns to be used from the CSV file
    columns = ['Points', 'Rebounds', 'Assists']

    # Read data from the CSV file into a Pandas DataFrame
    df = pd.read_csv(f'baller_files/gamepoints_{player_id}_{season}_{today_date}.csv', usecols=columns)


    ppg = round(df["Points"].mean(), 2)
    apg = round(df["Assists"].mean(), 2)
    rpg = round(df["Rebounds"].mean(), 2)


    df_last_6 = df.tail(6) 
    df_top_3 = df_last_6.head(3)
    df_last_3 = df_last_6.tail(3)

    l3_ppg = round(df_last_3["Points"].mean(), 2)
    l3_apg = round(df_last_3["Assists"].mean(), 2)
    l3_rpg = round(df_last_3["Rebounds"].mean(), 2)

    t3_ppg = round(df_top_3["Points"].mean(), 2)
    t3_apg = round(df_top_3["Assists"].mean(), 2)
    t3_rpg = round(df_top_3["Rebounds"].mean(), 2)

    # Plot the data
    df.plot()


    # Save the plot as an image file
    plt.savefig(f'baller_files/gamepoints_{player_id}_{season}_{today_date}.png', transparent=True)

    image_filepath = f'baller_files/gamepoints_{player_id}_{season}_{today_date}.png'


    return image_filepath, ppg, apg, rpg, l3_ppg, l3_apg, l3_rpg, t3_ppg, t3_apg, t3_rpg


# def post_image_to_s3():
#     s3_resource = boto3.resource(‘s3’)
#     s3_resource.meta.client.upload_file(
#         ‘/tmp/church_image.jpg’,
#         ‘bucket_name’,
#         ‘tests/church_image.jpg’,
#         ExtraArgs={‘ACL’: ‘public-read’})
        
def post_image_s3(image_filepath):
    bucket = 'baller-airflow-proj'
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
    s3.upload_file(image_filepath, bucket, image_filepath)
    s3.put_object_acl(Bucket=bucket, ACL='public-read', Key=image_filepath)
    url = f"https://{bucket}.s3.amazonaws.com/{image_filepath}"
    print(url)
    return url


def generate_report_commentary(player_full_name, ppg, apg, rpg, l3_ppg, l3_apg, l3_rpg, t3_ppg, t3_apg, t3_rpg, season):
    summary = f'In the {season} season so far, {player_full_name} has <strong>{ppg}</strong> points per game, <strong>{apg}</strong> assists per game, and <strong>{rpg}</strong> rebounds per game. '

    ppg_pct_change = round(((l3_ppg - t3_ppg)/t3_ppg)*100, 2)
    apg_pct_change = round(((l3_apg - t3_apg)/t3_apg)*100, 2)
    rpg_pct_change = round(((l3_rpg - t3_rpg)/t3_rpg)*100, 2)

    if ppg_pct_change > 0:
        ppg_trend = f'<p>Points per Game for {player_full_name} are trending upwards, <strong>growing {ppg_pct_change}%</strong> in recent games.</p> '
    else:
        ppg_trend = f'<p>Points per Game for {player_full_name} are trending downwards, <strong>decreasing {abs(ppg_pct_change)}%</strong> in recent games.</p> '

    if apg_pct_change > 0:
        apg_trend = f'<p>Lately, assists are improving, <strong>growing {apg_pct_change}%</strong> in recent games.</p> '
    else:
        apg_trend = f'<p>Lately, assists have been getting worse, <strong>decreasing {abs(apg_pct_change)}%</strong> in recent games.</p> '
    
    if rpg_pct_change > 0:
        rpg_trend = f'<p>Rebounds are on the upswing, <strong>growing {rpg_pct_change}%</strong> in recent games.</p> '
    else:
        rpg_trend = f'<p>Rebounds are fropping off, <strong>decreasing {abs(rpg_pct_change)}%</strong> in recent games.</p> '
    
    summary_text = summary + ppg_trend + apg_trend + rpg_trend
    return summary_text



def html_craft(url, player_full_name, team_logo, summary_text, season, player_id):
    f = open(f'html_files/{player_id}_{season}_{today_date}.html', 'w') 
    
    # the html code which will go in the file GFG.html 
    html_template = f"""

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html dir="ltr" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office" lang="en">
 <head>
  <meta charset="UTF-8">
  <meta content="width=device-width, initial-scale=1" name="viewport">
  <meta name="x-apple-disable-message-reformatting">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta content="telephone=no" name="format-detection">
  <title>New email template 2023-12-26</title><!--[if (mso 16)]>
    <style type="text/css">
    a {{text-decoration: none;}}
    </style>
    <![endif]--><!--[if gte mso 9]><style>sup {{ font-size: 100% !important; }}</style><![endif]--><!--[if gte mso 9]>
<xml>
    <o:OfficeDocumentSettings>
    <o:AllowPNG></o:AllowPNG>
    <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
</xml>
<![endif]--><!--[if !mso]><!-- -->
  <link href="https://fonts.googleapis.com/css2?family=Changa:wght@200;300;400;500;600;700;800&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,500;1,600;1,700;1,800&display=swap" rel="stylesheet"><!--<![endif]-->
  <style type="text/css">
.rollover:hover .rollover-first {{
  max-height:0px!important;
  display:none!important;
  }}
  .rollover:hover .rollover-second {{
  max-height:none!important;
  display:block!important;
  }}
  .rollover span {{
  font-size:0px;
  }}
  u + .body img ~ div div {{
  display:none;
  }}
  #outlook a {{
  padding:0;
  }}
  span.MsoHyperlink,
span.MsoHyperlinkFollowed {{
  color:inherit;
  mso-style-priority:99;
  }}
  a.es-button {{
  mso-style-priority:100!important;
  text-decoration:none!important;
  }}
  a[x-apple-data-detectors] {{
  color:inherit!important;
  text-decoration:none!important;
  font-size:inherit!important;
  font-family:inherit!important;
  font-weight:inherit!important;
  line-height:inherit!important;
  }}
  .es-desk-hidden {{
  display:none;
  float:left;
  overflow:hidden;
  width:0;
  max-height:0;
  line-height:0;
  mso-hide:all;
  }}
  .es-button-border:hover > a.es-button {{
  color:#ffffff!important;
  }}
@media only screen and (max-width:600px) {{*[class="gmail-fix"] {{ display:none!important }} p, a {{ line-height:150%!important }} h1, h1 a {{ line-height:120%!important }} h2, h2 a {{ line-height:120%!important }} h3, h3 a {{ line-height:120%!important }} h4, h4 a {{ line-height:120%!important }} h5, h5 a {{ line-height:120%!important }} h6, h6 a {{ line-height:120%!important }} h1 {{ font-size:40px!important; text-align:left }} h2 {{ font-size:28px!important; text-align:left }} h3 {{ font-size:18px!important; text-align:left }} h4 {{ font-size:24px!important; text-align:left }} h5 {{ font-size:20px!important; text-align:left }} h6 {{ font-size:16px!important; text-align:left }} .es-header-body h1 a, .es-content-body h1 a, .es-footer-body h1 a {{ font-size:40px!important }} .es-header-body h2 a, .es-content-body h2 a, .es-footer-body h2 a {{ font-size:28px!important }} .es-header-body h3 a, .es-content-body h3 a, .es-footer-body h3 a {{ font-size:18px!important }} .es-header-body h4 a, .es-content-body h4 a, .es-footer-body h4 a {{ font-size:24px!important }} .es-header-body h5 a, .es-content-body h5 a, .es-footer-body h5 a {{ font-size:20px!important }} .es-header-body h6 a, .es-content-body h6 a, .es-footer-body h6 a {{ font-size:16px!important }} .es-menu td a {{ font-size:14px!important }} .es-header-body p, .es-header-body a {{ font-size:14px!important }} .es-content-body p, .es-content-body a {{ font-size:14px!important }} .es-footer-body p, .es-footer-body a {{ font-size:12px!important }} .es-infoblock p, .es-infoblock a {{ font-size:12px!important }} .es-m-txt-c, .es-m-txt-c h1, .es-m-txt-c h2, .es-m-txt-c h3, .es-m-txt-c h4, .es-m-txt-c h5, .es-m-txt-c h6 {{ text-align:center!important }} .es-m-txt-r, .es-m-txt-r h1, .es-m-txt-r h2, .es-m-txt-r h3, .es-m-txt-r h4, .es-m-txt-r h5, .es-m-txt-r h6 {{ text-align:right!important }} .es-m-txt-j, .es-m-txt-j h1, .es-m-txt-j h2, .es-m-txt-j h3, .es-m-txt-j h4, .es-m-txt-j h5, .es-m-txt-j h6 {{ text-align:justify!important }} .es-m-txt-l, .es-m-txt-l h1, .es-m-txt-l h2, .es-m-txt-l h3, .es-m-txt-l h4, .es-m-txt-l h5, .es-m-txt-l h6 {{ text-align:left!important }} .es-m-txt-r img, .es-m-txt-c img, .es-m-txt-l img {{ display:inline!important }} .es-m-txt-r .rollover:hover .rollover-second, .es-m-txt-c .rollover:hover .rollover-second, .es-m-txt-l .rollover:hover .rollover-second {{ display:inline!important }} .es-m-txt-r .rollover span, .es-m-txt-c .rollover span, .es-m-txt-l .rollover span {{ line-height:0!important; font-size:0!important }} .es-spacer {{ display:inline-table }} a.es-button, button.es-button {{ font-size:14px!important; line-height:120%!important }} a.es-button, button.es-button, .es-button-border {{ display:inline-block!important }} .es-m-fw, .es-m-fw.es-fw, .es-m-fw .es-button {{ display:block!important }} .es-m-il, .es-m-il .es-button, .es-social, .es-social td, .es-menu {{ display:inline-block!important }} .es-adaptive table, .es-left, .es-right {{ width:100%!important }} .es-content table, .es-header table, .es-footer table, .es-content, .es-footer, .es-header {{ width:100%!important; max-width:600px!important }} .adapt-img {{ width:100%!important; height:auto!important }} .es-mobile-hidden, .es-hidden {{ display:none!important }} .es-desk-hidden {{ width:auto!important; overflow:visible!important; float:none!important; max-height:inherit!important; line-height:inherit!important }} tr.es-desk-hidden {{ display:table-row!important }} table.es-desk-hidden {{ display:table!important }} td.es-desk-menu-hidden {{ display:table-cell!important }} .es-menu td {{ width:1%!important }} table.es-table-not-adapt, .esd-block-html table {{ width:auto!important }} .es-social td {{ padding-bottom:10px }} .h-auto {{ height:auto!important }} }}
@media screen and (max-width:384px) {{.mail-message-content {{ width:414px!important }} }}
</style>
 </head>
 <body class="body" style="width:100%;height:100%;padding:0;Margin:0">
  <div dir="ltr" class="es-wrapper-color" lang="en" style="background-color:transparent"><!--[if gte mso 9]>
 <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
   <v:fill type="tile" src="https://ebzqijg.stripocdn.email/content/guids/CABINET_65537f22c5da57c992bf433adb4ccac3109de2d483c4d1838be624edcf60c046/images/image.png" color="transparent" origin="0.5, 0" position="0.5, 0"></v:fill>
 </v:background>
<![endif]-->
   <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" background="https://ebzqijg.stripocdn.email/content/guids/CABINET_65537f22c5da57c992bf433adb4ccac3109de2d483c4d1838be624edcf60c046/images/image.png" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-image:url(https://ebzqijg.stripocdn.email/content/guids/CABINET_65537f22c5da57c992bf433adb4ccac3109de2d483c4d1838be624edcf60c046/images/image.png);background-repeat:repeat;background-position:center top;background-color:transparent" role="none">
     <tr>
      <td class="es-m-margin" valign="top" style="padding:0;Margin:0">
       <table class="es-content" cellspacing="0" cellpadding="0" align="center" role="none" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:100%;table-layout:fixed !important">
         <tr>
          <td align="center" style="padding:0;Margin:0">
           <table class="es-content-body" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" role="none">
             <tr>
              <td align="left" style="padding:0;Margin:0">
               <table cellpadding="0" cellspacing="0" width="100%" role="none" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px">
                 <tr>
                  <td align="center" valign="top" style="padding:0;Margin:0;width:600px">
                   <table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px">
                     <tr>
                      <td align="center" height="112" style="padding:0;Margin:0"></td>
                     </tr>
                     <tr>
                      <td align="center" style="padding:20px;Margin:0;font-size:0px"><img class="adapt-img" src="{team_logo}" alt="" style="display:block;font-size:15px;border:0;outline:none;text-decoration:none" width="160" height="160"></td>
                     </tr>
                   </table></td>
                 </tr>
               </table></td>
             </tr>
             <tr>
              <td align="left" style="Margin:0;padding-top:20px;padding-right:20px;padding-bottom:40px;padding-left:20px;background-color:#fbf3ea" bgcolor="#fbf3ea">
               <table cellpadding="0" cellspacing="0" width="100%" role="none" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px">
                 <tr>
                  <td align="center" valign="top" style="padding:0;Margin:0;width:560px">
                   <table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px">
                     <tr>
                      <td align="center" class="es-m-txt-c" style="padding:10px;Margin:0"><h3 style="Margin:0;font-family:Changa, sans-serif;mso-line-height-rule:exactly;letter-spacing:0;font-size:22px;font-style:normal;font-weight:bold;line-height:26px;color:#333333">{player_full_name} ({season}) Stats</h3></td>
                     </tr>
                     <tr>
                     <td align="center" style="padding:0;Margin:0;font-size:0px"><img class="adapt-img" src="{url}" alt="" style="display:block;font-size:15px;border:0;outline:none;text-decoration:none" width="450" height="250"></td>
                     </tr>
                     <tr>
                      <td align="center" style="padding:0;Margin:0;padding-top:20px"><p style="Margin:0;mso-line-height-rule:exactly;font-family:Montserrat, sans-serif;line-height:23px;letter-spacing:0;color:#374769;font-size:15px">{summary_text}</p></td>
                     </tr>
                     <tr>
                      <td align="center" style="padding:0;Margin:0;padding-top:30px"><!--[if mso]><a href="https://www.little-ladder.com/" target="_blank" hidden>
	<v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" esdevVmlButton href="https://www.little-ladder.com/" 
                style="height:44px; v-text-anchor:middle; width:165px" arcsize="50%" stroke="f"  fillcolor="#fe991d">
		<w:anchorlock></w:anchorlock>
		<center style='color:#ffffff; font-family:arial, "helvetica neue", helvetica, sans-serif; font-size:14px; font-weight:700; line-height:14px;  mso-text-raise:1px'>LEARN MORE</center>
	</v:roundrect></a>
<![endif]--><!--[if !mso]><!-- --><span class="es-button-border msohide" style="border-style:solid;border-color:#ff564e;background:#fe991d;border-width:0px;display:inline-block;border-radius:30px;width:auto;mso-hide:all"><a href="https://www.little-ladder.com/" class="es-button" target="_blank" style="mso-style-priority:100 !important;text-decoration:none !important;mso-line-height-rule:exactly;color:#FFFFFF;font-size:14px;padding:14px 35px 14px 35px;display:inline-block;background:#fe991d;border-radius:30px;font-family:arial, 'helvetica neue', helvetica, sans-serif;font-weight:bold;font-style:normal;line-height:17px;width:auto;text-align:center;letter-spacing:0;mso-padding-alt:0;mso-border-alt:10px solid #fe991d">LEARN MORE</a></span><!--<![endif]--></td>
                     </tr>
                   </table></td>
                 </tr>
               </table></td>
             </tr>
           </table></td>
         </tr>
       </table>
       <table class="es-footer" cellspacing="0" cellpadding="0" align="center" role="none" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:100%;table-layout:fixed !important;background-color:transparent;background-repeat:repeat;background-position:center top">
         <tr>
          <td align="center" style="padding:0;Margin:0">
           <table class="es-footer-body" cellspacing="0" cellpadding="0" bgcolor="#ffffff" align="center" role="none" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:#E33650;width:600px">
             <tr>
             
             </tr>
           </table></td>
         </tr>
       </table>
       <table cellpadding="0" cellspacing="0" class="es-content" align="center" role="none" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;width:100%;table-layout:fixed !important">
         <tr>
          <td align="center" style="padding:0;Margin:0">
           <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" bgcolor="#c9dcff" align="center" role="none">
             <tr>
              <td style="Margin:0;padding-right:20px;padding-left:20px;padding-top:30px;padding-bottom:30px;background-position:left top" align="left">
               <table width="100%" cellspacing="0" cellpadding="0" role="none" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px">
                 <tr>
                  <td valign="top" align="center" style="padding:0;Margin:0;width:560px">
                   <table width="100%" cellspacing="0" cellpadding="0" role="none" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px">
                     <tr>
                      <td align="center" style="padding:0;Margin:0;display:none"></td>
                     </tr>
                   </table></td>
                 </tr>
               </table></td>
             </tr>
           </table></td>
         </tr>
       </table></td>
     </tr>
   </table>
  </div>
 </body>
</html>


"""
    
    # writing the code into the file 
    f.write(html_template) 
    
    # close the file 
    f.close() 




if __name__ == "__main__":
  with open('email_list.csv', newline='') as file: 
    
    reader = csv.reader(file, delimiter = ',') 
      
    headings = next(reader) 
      
    Output = [] 
    for row in reader: 
        Output.append(row[:]) 
  

request_stack = []
dedup_request_stack = []
for x in Output: 
    a = x[2]
    b = x[3]
    request_stack.append([a,b])

for elem in request_stack:
    if elem not in dedup_request_stack:
        dedup_request_stack.append(elem)

for x in dedup_request_stack:
  player_id = x[0]
  season = x[1]


    # Make an API request for player statistics
  PLAYER_DATA_RESPONSE, player_id, season = hit_nba_api(player_id, season)

    # Write player data to a CSV file
  player_id, season, player_full_name, team_logo = write_player_data_csv(PLAYER_DATA_RESPONSE, player_id, season)

    # Draw a graph based on the player data
  image_filepath, ppg, apg, rpg, l3_ppg, l3_apg, l3_rpg, t3_ppg, t3_apg, t3_rpg = draw_graph(player_id, season)

  url = post_image_s3(image_filepath)

  summary_text = generate_report_commentary(player_full_name, ppg, apg, rpg, l3_ppg, l3_apg, l3_rpg, t3_ppg, t3_apg, t3_rpg, season)

  html_craft(url, player_full_name, team_logo, summary_text, season, player_id)

  os.remove(f"baller_files/gamepoints_{player_id}_{season}_{today_date}.png")
  os.remove(f"baller_files/gamepoints_{player_id}_{season}_{today_date}.csv")
  



# Generate and send email --> 