import requests
import re
import smtplib
import ssl
import WatchWatcher
from bs4 import BeautifulSoup

type(None) == None.__class__

special_words = ["alpine", "alpinist", "zimbe"] #special words override, if one of these words is in title, it will ignore the price cutoff
brands = ["seiko"]
diameter_cutoff = 43
price_cutoff = 225

case_winder_words = ["case", "cases", "winder", "winders", "display valet"] #key words for a display case or watch winder
watch_words = ["watch", "watches"]
strap_words = ["strap", "straps"]

show_straps = False
show_cases = False
show_watches = True

def main():
    #use cookie to create the main session
    session = requests.Session()
    jar = requests.cookies.RequestsCookieJar()
    refresh_token = get_refresh_token()
    jar.set("refreshToken", refresh_token) #sets the login cookie, alloowing us to view products
    session.cookies = jar #set the cookie

    #gets html for main watch store page
    starting_link = "https://drop.com/watches/drops"
    soup = get_and_parse_url(starting_link, session)
    print("viewing watch page...")
    #print(soup.prettify())

    #gathers all the links to each individual watch/strap/case/winder
    buy_links = []
    master_list = soup.find("div", class_ = "massdrop__scroll_loader")
    if master_list is None: #detects errors getting watch list html (not due to redirect)
        print("error getting master watch list")
        exit(1)
    for link in master_list.find_all('a'):
        #print(link.get('href'))
        if("talk#discussions" not in link.get('href')):
            buy_links.append("https://drop.com" + link.get('href') + "/details#details")

    #for link in buy_links: #test print all the links
        #print(link)

    all_products = [] #will hold Watch, Case, and Stap objects (which are all products)
    
    for link in buy_links: #loop through each individual link
        #print(link)
        store_item_html = get_and_parse_url(link, session)
        base_price = store_item_html.find("div", class_ = re.compile("wdio__price*")).get_text()[1:] #gets the sale price of item
        item_title = store_item_html.find("div", class_ = re.compile("Text__type--title*")).get_text()
        #print(item_title)
        model_list = store_item_html.find("div", class_ = re.compile("DetailSection__detail_list*"))
        print(item_title, base_price)

        #find the type of the product and send it to be handled
        type_found = False
        for word in case_winder_words:
            if word in item_title.lower():
                all_products = all_products + handle_case(store_item_html, item_title, base_price, link)
                type_found = True
                break
        if not type_found:
            for word in watch_words:
                if word in item_title.lower():
                    all_products = all_products + handle_watch(store_item_html, item_title, base_price, link)
                    type_found = True
                    break
        if not type_found:
            for word in strap_words:
                if word in item_title.lower():
                    handle_strap(store_item_html, item_title, base_price, link)
                    type_found = True
                    break


    #filter_and_send_products(all_products)



def filter_and_send_products(products):
    printed_watches = []
    for product in products:
        is_special = False
        for word in special_words:
            if word in product.title:
                product.print_product()
                is_special = True
                break
        if is_special:
            continue
        if int(product.size) <= diameter_cutoff and int(product.price) <= price_cutoff:
            product.print_product()



#gets html for main urls
#uses the global cookie
def get_and_parse_url(url, session):
    r = session.get(url)
    if r.url != url: #detect if url was redirected
        print("Error: link was temporarily redirected. Cannot parse url")
        exit(1)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup

def handle_case(store_item_html, title, price, link):
    products = []
    model_list = store_item_html.find("div", class_ = re.compile("DetailSection__detail_list*"))
    model_names = get_model_names(model_list)
    if len(model_names) == 0:
        #handle differently for single item
        model_name = get_single_model_name(model_list)
        case = WatchWatcher.Case(title, model_name, price, link)
        products.append(case)
    else:
        for name in model_names:
            case = WatchWatcher.Case(title, name, price, link)
            products.append(case)
    return products

def handle_strap(store_item_html, title, price, link):
    print("strap")
    model_list = store_item_html.find("div", class_ = re.compile("DetailSection__detail_list*"))
    '''
    if len(get_model_names(model_list)) == 0:
        #handle differently for single item
    else:
        #handle multiple items
    '''

def handle_watch(store_item_html, title, price, link):
    model_list = store_item_html.find("div", class_ = re.compile("DetailSection__detail_list*"))
    products = []

    previous_water_res = 0
    previous_size = 0
    previous_band_material = ""
    for ul in model_list.find_all("ul"): #multiple ul's means multiple models/options for same listing
        water_res = 0
        size = 0
        band_material = ""
        for li in ul.find_all("li"):
            if "case width" in li.get_text().lower() or "case size" in li.get_text().lower() or "case diameter" in li.get_text().lower():
                size = get_watch_size(li)
                if size == 0:
                    size = previous_size
            elif "water resistant" in li.get_text().lower() or "water resistance" in li.get_text().lower():
                water_res = get_watch_water_res(li)
                if water_res == 0:
                    water_res = previous_water_res
            elif "band material" in li.get_text().lower() or "band:" in li.get_text().lower():
                band_material = li.get_text().split(":")[1]
                if band_material == "":
                    band_material = previous_band_material
        product = WatchWatcher.Watch(title, price, size, band_material, water_res, link)
        products.append(product)
        previous_band_material = band_material
        previous_size = size
        previous_water_res = water_res

    return products
    

#only returns populated list if there are multiple different models
def get_model_names(model_list):
    model_names = []
    for name in model_list.find_all("strong"): #get the model names
        #print(name.get_text())
        model_names.append(name.get_text())
    return model_names

def get_single_model_name(model_list):
    lis = []
    for ul in model_list.find_all("ul"):
        for li in ul.find_all("li"):
            lis.append(li.get_text())
    return lis[0]

def get_watch_size(li):
    temp = re.findall(r'\d+', li.get_text())
    res = list(map(int, temp))
    return res[0]

def get_watch_water_res(li):
    return get_watch_size(li)


#gets the refresh token for the cookie from a file
#this is needed in order to view products
def get_refresh_token():
    fo = open("refresh_token.txt", "r")
    line = fo.readline()
    fo.close()
    return line



if __name__ == "__main__":
    main()