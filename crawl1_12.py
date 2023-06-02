# %%
import requests
from requests.exceptions import ProxyError
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import time
from numpy.random import default_rng
from random import randint
from numpy import nan 

# from emoji import replace_emoji #for remove emoji from description


# %%
class Extract_link_page:
    def __init__(self,n_page , primary_link) :
        self.number_of_pages = n_page
        self.primary_link = primary_link
    def Extract(self,page_count_auto_save=50,save_end=False,show_time=False ,return_links=False, show_page=False,show_duplicate=False,random_request=False):
        
        if show_time: t=time.time() ; t1=time.time()
        
        link_page=[]
        file_name_list=[]
           
        for i in range(0,self.number_of_pages):
                # time.sleep(1)
                # if break_>10:break
                html=requests.get(self.primary_link+str(i))
                if html.status_code == 200:

                    soup=BeautifulSoup(html.content,'html.parser')
                    
                    if show_page :print("page :" , i)

                    links=soup.find_all('a',class_="kilid-listing-card flex-col al-start ng-star-inserted", href=True)
                    if len(links)<10: print("tedad link break") ; continue

                    # else:print(links)
                    for a in links:
                        # sleep(0.2)
                        if a["href"] in link_page:
                            if show_duplicate:print("duplicate in page :",i)
                            n_duplicate +=1
                            continue
                        else:
                            link_page.append(a["href"])
                        # print("Found the URL:", a['href'])
                if (i % page_count_auto_save == 0) and (i!=0) and(page_count_auto_save != 0):
                 
                    file_name = "link_total_%s.txt"%time.strftime("%B_%d %H_%M_%S")

                    with open(file_name,"w") as f:
                        f.write(",".join(link_page))
                        f.close()          
                    file_name_list.append(file_name)
                
                if len(file_name_list) >1:
                       os.remove(file_name_list[-2])
                
                  
                if random_request:    
                    rand=  default_rng().uniform(6,11) 
                    time.sleep(rand)
                    print('random request time = %d' %rand) 
                if show_time:
                    print(f'time this request = {round(time.time()-t,3)}')
                    t=time.time()
                    print(f"total time = {round(time.time()-t1,3)}")
        if save_end:
            with open("link_total_%s.txt"%time.strftime("%B_%d %H_%M_%S"),"w") as f:
                    f.write(",".join(link_page))
                    f.close()  
            
        if return_links:
            return link_page
            # print(link_home)
        
    

# %%
# t1 = Extract_link_page(2, "https://kilid.com/buy/tehran?listingTypeId=1&page=")
# t1.Extract(n_auto_saving=50 ,show_duplicate=True,show_page=True,show_time=True,random_request=True,return_links=True,)

# %%


# %%
class Extract_informations:
   
      def __init__(self,links):
         self.list_links= links
         self.start=None
      

      def replace_chars(self,text):
         for ch in ['/','`','*','_','{','}','[',']','(',')','>','#','+','-','!','$','\'',"//"]:
              if ch in text:
                  text = text.replace(ch," ")
         return text

      def try_css_selector(self,soup,css):

          try:
              return self.replace_chars(soup.select_one(css).text.strip())

          except AttributeError:
              return None
      
      def extract_location(self,soup,css):
         
         try:
            location=dict()
            total_loc=[]
            total_loc = self.try_css_selector(soup,css).split("،")
         except: 
            location["region"]=None
            location["city"]=None
            location["address"]=None
            return location
         else:
            region=[]
            for i in total_loc[1].strip():
               if i.isdigit():
                  region.append(i)
            try: location["city"]=total_loc[0].strip()
            except :  location["city"]=None
            try:  location["region"]="".join(region)
            except: location["region"]=None
            try:  location["address"]=total_loc[2].strip()
            except:  location["address"]=None

            return location
         

      def extract_features(self,soup,css):
         features=dict()
         features2=dict()
         name=[]
         nums=[]
         try:
            for i in self.try_css_selector(soup,css).split():
               if i.isalpha():
                  name.append(i)
               else:nums.append(i)

            features={k:v for k,v in zip(name,nums)}

            features2["parking"] = features.get("پارکینگ",None)    
            features2["Meterage"] = features.get("متر",None)    
            features2["bedroom "] = features.get("خوابه",None)    
            features2["age_year"] = features.get("ساله",None)    

         except:
            features2["parking"] = None 
            features2["meterage"] = None
            features2["bedroom "] = None    
            features2["age_year"] = None    

         return features2


      def extract_persian_text(self,soup, css):
         try:
            string_=str(soup.select_one(css))

            facilities=[]
            pattern =r'.*>([\u0600-\u06FF]+\s*[\u0600-\u06FF]*)<.*'
            while True:
                try:
                    y=re.search(pattern,string_)
                    if y.groups():
                        facilities.append(y.groups()[0])
                        string_=string_.replace(facilities[-1],"")          
                    else:break

                except  : break


            return " , ".join(facilities)

         except: return None

      def extract_number(self,soup,css):
         try:
            for i in self.try_css_selector(soup=soup,css=css).split():
               if i.isdigit():
                  return int(i)
         except:
            return None


      def details(self,href):
         try:
            html = requests.get(href)
            
         except ProxyError:
            sleep=randint(40,120)
            print(f"erore conection ################ sleep= {sleep}")
            print(sleep)
            time.sleep(sleep)
            return self.details(href)
         else:
            html_status = html.status_code == 200
            if html_status:
               soup = BeautifulSoup(html.content , "html.parser")

               home=dict() 
               home["title"]= self.try_css_selector(soup,".single-data__info")  
               try:
                  home["total_price"]=self.replace_chars(self.try_css_selector(soup,".single-data__container.ng-star-inserted").split()[2])
               except:
                  home["total_price"]=None

               home["price_per_meter"]=self.extract_number(soup=soup,css=".ng-star-inserted+ .single-data__container")

               # home=self.merge_dic(home,self.extract_location(soup=soup , css=".single-data__location span"))
               loc = self.extract_location(soup,".single-data__location span")
               home=home|loc
               # home=self.merge_dic(home,self.extract_features(soup,".single-data__location span"))
               features= self.extract_features(soup,".single-data__container--attributes")
               home=home|features
               home["facilities"] = self.extract_persian_text(soup,".ng-trigger-slideDown")
               home["adviser"] = self.try_css_selector(soup=soup , css= ".single-sticky__department__user-name")
               home["real_estate"] =self.try_css_selector(soup=soup,css=".single-sticky__department__name")
               home["ad_code"] = self.extract_number(soup=soup,css=".single-sticky__info__item:nth-child(1)")
               # home["description"] = self.extract_persian_text(soup,".single-description")
               # try: home["description"] = replace_emoji(soup.select_one(".single-description").text.strip())
               # except:   home["description"] = None


               return home , html_status
            return None , None

                  
      def scrap_with_start_end(self,df=pd.DataFrame(),n_pre_scrap=None,myfile_pre=None,primary_link ="https://kilid.com" ,start=10000,end=21000,auto_end=True,random_request=True,show_time=True):
               
               if auto_end:
                  end = start+1000
               
               if show_time: t=time.time() ; t1=time.time()   
               for url in range(start,end):
                  if n_pre_scrap:
                     print("link number = %d" %(url+n_pre_scrap))
                  else:
                     print("link number = %d" %url)
                  href = primary_link+self.list_links[url]
                  
                  detail,html_status=self.details(href)
                  if detail and html_status:
                     output=pd.DataFrame(detail,index=[0])
                     print(detail["title"])
                     if output.isna().sum().sum() >10: continue
                     myfile = "homes_not_clean_%s.xlsx"%time.strftime("%B_%d %H_%M_%S")
                     df=pd.concat([df,output],axis=0,ignore_index=True)
                     df.to_excel(myfile,index=None)
                     
                     myfile_pre =self.name_last_excel(pos=-2)
                     if myfile_pre :
                        os.remove(myfile_pre)
                           
                  else:
                     txt_name=self.name_last_excel(prefix_name="link_total")
                     
                     with open(txt_name,"w") as f:
                           self.list_links.pop(url)
                           
                           f.write(" ".join(self.list_links))
                           f.close()  
                           
                     
                     rand=  default_rng().uniform(1,4) 
                     print('null request random request time = %d' %rand)    
                     # time.sleep(rand)
                     continue

                  if random_request:    
                     rand=  default_rng().uniform(random_request[0],random_request[1]) 
                     print('random request time = %d' %rand)    
                     time.sleep(rand)
                     
                  if show_time:
                     print(f'time this request = {round(time.time()-t,3)}')
                     t=time.time()
                     print(f"total time = {round(time.time()-t1,3)}")
                     
                     # print(myfile +" "+len(files_name) )
                        

                     # print(len(files_name))
                    
                  
                  
                  
               
            
      def data_cleaning(self,df):
        
         x=[]
         
         for i in df.facilities[df.facilities.notna()].str.split(" , "):
           for j in i:
         
             x.append(j)
         x=list(set(x))
         len(x)
         y ="""'sauna',
           'proportionate shares',
           'roof garden',
           'balcony',
           'sports hall',
           'exchange',
           'guardian',
           'agreed price',
           'Elevator',
           'Jacuzzi',
           'have loan',
           'conference hall',
           'newly built',
           'mall',
           'lobby',
           'remote door',
           'air conditioning',
           'pool',
           'Central antenna',
           'Warehouse'
           """

         dict_unique_features=dict(zip(x,[i.strip().replace(" ","_") for i in y.replace("\n","").replace("'","").split(", ")]))
         dict_unique_features

         temp=dict()
         for i in range(df.shape[0]):
           list_features=[]
           for j in dict_unique_features.keys():
             if df.facilities[i] is nan: 
                 list_features.append(nan)
                 continue
              
             if j in df.facilities[i].split(" , "):
               list_features.append(1)
             else :
               list_features.append(0)
           temp[i]=list_features
         facilities=pd.DataFrame(temp.values(),columns=dict_unique_features.values(),index=temp.keys())

         
         del temp
         del list_features
         
         df2=pd.concat([df,facilities],axis=1).drop("facilities",axis=1)
         myfile = "homes_cleaned_%s.xlsx"%time.strftime("%B_%d %H_%M_%S")
         df2.to_excel(myfile,index=None)
         
         return df2

      def continue_previous_req(self,start):
         
                files_name=self.name_last_excel("homes_not_clean_")
                print(files_name)
                if files_name:
                   df = pd.read_excel(files_name)
                   link_number="/buy/detail/" +str(int( df.iloc[-1,:]["ad_code"]))
                else:
                   files_name=None
                   df = None
                   link_number = None

                if link_number :
                   try:
                      start = self.list_links.index(link_number) + 1
                   except:
                      pass
                   
                return start , files_name , df
             
      def name_last_excel(self,prefix_name="homes_not_clean_",pos=-1):
                files_name=[filename for filename in os.listdir('.') if filename.startswith(prefix_name)]
                if files_name:
                  try:
                   return  files_name[pos]
                  except IndexError:
                     return None
                return None
         
      def remove_link(self):
            files_name = self.name_last_excel("homes_not_clean_")
            
            if files_name:
               df = pd.read_excel(files_name)
               make_link=lambda i : "/buy/detail/" + str(int(i))

               df.dropna(subset=["ad_code"],inplace=True)
               pre_link = df.ad_code.apply(make_link).tolist()
               new_link = list(filter (lambda i : i not in pre_link , self.list_links))
               self.list_links = new_link
               len_ = len(pre_link)
            else :  
               len_ = 0
               
            return len_

# %%


with open("link_total_19_15_32.txt","r") as f:
  
      link_homes=f.read().split()
      
homes=Extract_informations(link_homes)

random_request_time=(5,10)
# change start , end 👇👇👇👇
start  = 10000 
end = 16000    #len(link_homes)

n_pre_scrap=homes.remove_link()

start ,myfile_pre, df = homes.continue_previous_req(start)


homes.scrap_with_start_end(df=df ,n_pre_scrap=n_pre_scrap,myfile_pre=myfile_pre,start= start,end=end , auto_end=True ,random_request=random_request_time,show_time=True)
           

            
            


# %%
# df=pd.read_excel(homes.name_last_excel())
# df.region.value_counts().sort_index()

# %%
# after finish work run this
'''

df = pd.read_excel(df.read_homes.name_last_excel("homes_not_clean_"))
df_clean = homes.data_cleaning(df)
df_clean.to_excel("homes_cleaned.xlsx",index=None)
'''


