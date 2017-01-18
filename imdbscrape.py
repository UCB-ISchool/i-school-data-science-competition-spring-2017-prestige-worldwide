import urllib.request as req
import pprint as pp
import re
import datetime

from bs4 import BeautifulSoup


class Person:
	def __init__(self,name,id=None):
		self.name = name
		# If the person does not have an IMDB page, their id is None
		self.id = id

	def __str__(self):
		desc = '<Person: ' + self.name
		if self.id is not None:
			desc += ' (' + self.id + ')'
		else:
			desc += ' (None)'
		desc += '>'
		return desc

	def __repr__(self):
		return(str(self))


class Marriage:
	def __init__(self,person1,person2,start,end=None):
		self.person1 = person1
		self.person2 = person2
		self.start = start
		self.end = end
		self.divorced = False
		self.num_children = 0

	def __repr__(self):
		desc = '<Marriage: (' + str(self.person1) + ' ' + (str(self.person2)) + ')'
		desc += ' divorced = ' + str(self.divorced)
		desc += ' (' + str(self.days_married()) + ' days)'
		desc += ', num_children = ' + str(self.num_children)
		desc += '>'
		return desc

	def days_married(self):
		start = self.start
		end = self.end if self.end is not None else datetime.datetime.now()
		return (end - start).days


def soup_for_url(url):
	''' Gets the content of a web page '''
	try:
		response = req.urlopen(url, timeout=15)
		content = response.read().decode("utf-8")
		# Remove extra spaces between HTML tags.
		content = ''.join([line.strip() for line in content.split('\n')])
		response.close()
	except:
		return None
	return BeautifulSoup(content, 'html.parser')


def person_from_soup(soup):
	''' Checks the soup for the page's biographical info '''
	name = soup.head.find('meta', property='og:title')['content']
	uid = soup.head.find('meta', property='pageId')['content']
	return Person(name, uid)


def marriages_from_soup(soup):
	''' Checks a html soup for spouses.
		Returns an empty array if there are none.
		Returns None if an error occurred '''
	person1 = person_from_soup(soup)

	marriages = []
	spouse_table = soup.find(id='tableSpouses')
	if spouse_table == None:
		return spouses
	for spouse_row in spouse_table:		
		spouse_name = ''
		spouse_id = None
		spouse_start = 0
		spouse_end = 0

		spouse_name_item = list(spouse_row)[0]
		# If there is no hyperlink to the spouse, just get the string
		if spouse_name_item.string is not None:
			spouse_name = spouse_name_item.string
		else:
			spouse_name = spouse_name_item.find('a').string
			spouse_id = spouse_name_item.find('a')['href'].split('/')[2].split('?')[0]
		person2 = Person(spouse_name.lstrip().rstrip(), spouse_id)

		spouse_date_item = list(spouse_row)[1]
		spouse_date_str = ''.join([child.string for child in spouse_date_item.children])
		spouse_date_str = re.sub("  +" , "", spouse_date_str.replace(u'\xa0', u' '))

		marriage_data = [item.strip('()') for item in re.split('([^()]+)', spouse_date_str) if len(item.strip('()')) > 1]
		did_divorce = False
		num_children = 0
		for m in marriage_data:
			if m.find('divorce') != -1:
				did_divorce = True
			elif m.find('child') != -1:
				# Yes, this does not work for 10+ children
				num_children = int(m[0])

		marriage_dates = marriage_data[0].split('-')
		marriage_start = _convert_string_to_date(marriage_dates[0])
		# This means that any marriage in which a person dies or somehow leaves sans divorce will be ignored
		marriage_end = _convert_string_to_date(marriage_dates[1]) if did_divorce == True else None

		marriage = Marriage(person1, person2, marriage_start, marriage_end)
		marriage.divorced = did_divorce
		marriage.num_children = num_children
		marriages.append(marriage)
	return marriages


def _convert_string_to_date(string):
	return datetime.datetime.strptime(string,'%d %B %Y')


def main():
	emma_stone = 'http://www.imdb.com/name/nm1297015/bio?ref_=nm_ov_bio_sm'
	tom_cruise = 'http://www.imdb.com/name/nm0000129/bio?ref_=nm_ov_bio_sm'
	scarlett_johansson = 'http://www.imdb.com/name/nm0424060/bio?ref_=nm_ov_bio_sm'
	bs  = soup_for_url(scarlett_johansson)
	pp.pprint(marriages_from_soup(bs))


if __name__ == '__main__':
    main()
