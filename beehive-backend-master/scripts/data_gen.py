import requests
from lxml import html, etree

def generate_sample_xpath(tree):
    element_tree = etree.ElementTree(tree)
    for e in tree.iter():
        xpath = element_tree.getpath(e)
        items = tree.xpath(xpath + '/text()')

        for item in items:
            clean_item = item.strip().strip('\n').strip()
            
            if clean_item and 'Natural Genetic Variation' in clean_item:
                print(f'xpath: {xpath} => {clean_item}')

def get_html_tree(url):
    page = requests.get(url)
    tree = html.fromstring(page.content)

    return tree

def get_field(tree, xpath):
    return tree.xpath(xpath)


def main():
    # tree = get_html_tree('https://www.biorxiv.org/content/10.1101/737619v2')
    tree = get_html_tree('https://www.biorxiv.org/content/10.1101/2020.05.21.109371v1')
    
    generate_sample_xpath(tree)

    print(get_field(tree, '/html/body/div[2]/section/div/div/div/div/div/div/div/div/div[2]/div/div/div[5]/div/div/div/div[2]/div/div/div[7]/div/div/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div/text()'))



if __name__ == '__main__':
    main()
