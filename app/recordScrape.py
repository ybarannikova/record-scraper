__author__ = "ybarannikova"

import requests, csv, re
from lxml import html

genre_urls = {
    'jazz': "http://www.planetmusic33.com/jazz-music/",
    'rock': "http://www.planetmusic33.com/rock-music/",
    'electronic': "http://www.planetmusic33.com/electronic/"
}

class RecordScraper():

  def __init__(self):
    self.detailed = False
    self.genre = "jazz"

  def getRecords(self, url):
    """Collects data about all records in a certain category
    """
    response = requests.get(url)
    page = html.fromstring(response.content)
    records = page.xpath("//div[@class='Content Wide ']")
    # pagination
    for a in page.xpath("//div[@id='CategoryPagingTop']/div[@class='CategoryPagination']/ul[@class='PagingList']/li/a"):
      page = html.fromstring(requests.get(a.attrib['href']).content)
      records.append(page.xpath("//div[@class='Content Wide ']")[0])
    return records

  def getDetails(self, url):
    """Collects detailed information about a certain record
    """
    response = requests.get(url)
    page = html.fromstring(response.content)
    details = page.xpath("//div[@id='ProductDescription']")[0]
    return details

  def readRecords(self, records):
    """Constructs dictionaries with records' information
    """
    for div in records:
      for record in div.xpath("//div[@class='prod-inner']"):
        url = record.xpath(".//a")[0].attrib['href']
        details = record.xpath(".//a[@class=' pname']")[0].text
        # use regex to parse record's details string into name and label
        match = re.search(r'(.+) - (.*)', details)
        record_dict = {
          'name': match.group(1) if match else details,
          'label': match.group(2) if match else None,
          'url': url,
          'img': record.xpath(".//img")[0].attrib['src'],
          'price': record.xpath(".//em[@class='p-price']")[0].text
        }
        if self.detailed:
          details = self.getDetails(url)
          # description can be located in different DOM elements
          description = details.xpath(".//p/span/span/span") or details.xpath(".//p/span/strong")or details.xpath(".//p/span") or details.xpath(".//p")
          tracklist = ", ".join(i.text for i in details.xpath(".//span[@class='tracklist_track_title']"))
          record_dict.update({
            'description': description[0].text if description else None,
            'tracklist': tracklist
          })
        clean_record_dict = self.cleanRecordDict(record_dict)
        yield clean_record_dict

  def cleanRecordDict(self, record_dict):
    """Cleans record dictionary. Currently, this method only takes care of decoding ASCII characters.
    """
    return {k:v.encode("utf-8") if v else None for k,v in record_dict.iteritems()}


  def writeRecords(self, records):
    """Writes collected data into a CSV file
    """
    with open('records.csv', 'w') as csvfile:
      if self.detailed:
        fieldnames = ['name', 'label', 'price', 'url', 'img', 'description', 'tracklist']
      else:
        fieldnames = ['name', 'label', 'price', 'url', 'img']
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writeheader()
      writer.writerows(record for record in records)


  def main(self):
    if self.detailed:
      print "Collecting detailed information..."
    category_url = genre_urls[self.genre]
    records = self.getRecords(category_url)
    records_iterator = self.readRecords(records)
    write_to_csv = self.writeRecords(records_iterator)