import logging
import requests 
# 
# 1. get info by doi
# 2. get info by title

logging.basicConfig()
logger = logging.getLogger('crossref')
logger.setLevel(logging.DEBUG)
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'}

class crossrefInfo(object):
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS
        self.base_url = "http://api.crossref.org/"

    def set_proxy(self, proxy=None):
        """set proxy for session
        
        Args:
            proxy (str): The proxy adress. e.g 127.0.1:1123
        Returns:
            None
        """
        if proxy:
            self.sess.proxies = {
                "http": proxy,
                "https": proxy, }
            
    
    def extract_json_info(self, bib):
        """Extract bib json information from requests.get().json()
        
        Args:
            bib (json object): obtained by requests.get().json()
        
        Returns:
            A dict containing the paper information.
        """
        pub_date = [str(i) for i in bib['published']["date-parts"][0]]
        pub_date = '-'.join(pub_date)

        if 'author' in bib.keys():
            authors = ' ,'.join([i["family"]+" "+i['given'] for i in bib['author'] if "family" and "given" in i.keys()])
        else:
            authors = "No author"
        
        journal_name=""
        proc_name=""
        conference_name=""

        work_type = bib.get('type')
        if work_type == 'journal-article':
            journal_titles = bib.get('container-title', [])
            if journal_titles:
                journal_name = journal_titles[0]
        elif work_type in ['proceedings', 'proceedings-article']:
            proc_titles = bib.get('container-title', [])
            if proc_titles:
                proc_name = proc_titles[0]
            event = bib.get('event', {})
            if event:
                conference_name = event.get('name')

        bib_dict = {
            "title": bib['title'][0],
            "author": authors,
            "journal": journal_name if journal_name!='' else conference_name,
            "year": pub_date,
            "url": bib["URL"],
            "pdf_link": bib["link"][0]["URL"],
            "cited_count": bib["is-referenced-by-count"]
        } 
        
        return bib_dict


    def get_info_by_doi(self, doi):
        """Get the meta information by the given paper DOI number. 
        
        Args:
            doi (str): The paper DOI number
            
        Returns:
            A dict containing the paper information. 
            {
                "title": xxx,
                "author": xxx,
                "journal": xxx,
                etc
            } 
            OR
            None
        """
        url = "{}works/{}"
        url = url.format(self.base_url, doi)
        
        try:
            r = self.sess.get(url)

            bib = r.json()['message']
            return self.extract_json_info(bib)
            
        except:
            logger.error("DOI: {} is error.".format(doi)) 
            
    
    def get_info_by_title(self, title):
        """Get the meta information by the given paper title. 
        
        Args:
            doi (str): The paper title
            
        Returns:
            A dict containing the paper information. 
            {
                "title": xxx,
                "author": xxx,
                "journal": xxx,
                etc
            }
            OR
            None
            OR
            A list [{}, {}, {}]
        """
        url = self.base_url + "works"
        params = {"query.bibliographic": title, "rows": 20}
        try:
            r = self.sess.get(url, params=params)
            items = r.json()["message"]["items"]
            
            for i, item in enumerate(items):
                
                title_item = item['title'][0]
                try:
                    title_item = title_item.decode("utf-8")
                except:
                    pass
            
                item["title"][0] = title_item

                if title_item.lower() == title.lower():
                    return self.extract_json_info(item)
                
                items[i] = item

            return [self.extract_json_info(it) for it in items]
        except:
            logger.error("Title: {} is error.".format(title)) 
            
            
if __name__ == "__main__":
    doi = "10.1145/3694715.3695964"
    # title = "Heterogeneous Graph Attention Network"
    # title = "Learning to Copy Coherent Knowledge for Response Generation"
    
    crossref_info = crossrefInfo()
    # crossref_info.set_proxy(proxy="127.0.1:1123")
    
    bib_doi = crossref_info.get_info_by_doi(doi)
    # bib_title = crossref_info.get_info_by_title(title)
    
    print(bib_doi)
    print("\n")
    # print(bib_title)
