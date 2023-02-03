import sys

# setting path
sys.path.append('../seller-plus-gui')

from global_variables import *
from global_functions import *

from tools_functions.general import *

from database_functions.compare_results import *
from database_functions.compare_searches import *

def get_pricing_info_for_asins(marketplace_id: str, asins_list: list) -> dict:
    """
    Args:
        marketplace_id (str): Marketplace Identifier
        asins_list (list): List Contains Asins

    Returns:
        dict: Returns a dict of products contains required information.
    """
    return_dict = {}
    country_code = MARKETPLACE_ID_TO_COUNTRY_CODE[marketplace_id]
    credentials, marketplace = get_credentials_and_marketplace_by_country(country_code)
    res = Products(credentials=credentials, marketplace=marketplace)
    
    # Create an inner function to be used in retry_function_for_quote_exceed_sp_api
    def inner_func():
        return res.get_competitive_pricing_for_asins(asins_list, MarketplaceId=marketplace_id).payload
    
    # Try to get the result from the inner function
    try:
        result = retry_function_for_quote_exceed_sp_api(inner_func)
    except Exception as error:
        return return_dict
    
    for item in result:
        # empty dict to be returned if the item is not successful
        empty_dict = {
            'marketplace_id': marketplace_id,
            'asin': item['ASIN'],
            'price': {
                'landed_price': {
                    'Amount': 0,
                    'CurrencyCode': ''
                },
                'listing_price': {
                    'Amount': 0,
                    'CurrencyCode': ''
                },
                'shipping_price': {
                    'Amount': 0,
                    'CurrencyCode': ''
                }
            },
            'pricing_message': 'No Competitive Pricing'
        }
        
        # If the item is not successful, return an empty dict
        if (item['status'] != 'Success'):
            return_dict[item['ASIN']] = empty_dict
            continue
        
        # If the item is successful but there is no competitive pricing, return an empty dict
        if (len(item['Product']['CompetitivePricing']['CompetitivePrices']) == 0):
            return_dict[item['ASIN']] = empty_dict
            continue
        
        # If the item is successful and there is competitive pricing, return a dict with the pricing info
        '''
        marketplace_id: str
        asin: str
        price: dict (keys=['LandedPrice', 'ListingPrice', 'Shipping'])
        sales_rankings: list
        '''
        asin = item['Product']['Identifiers']['MarketplaceASIN']['ASIN']
        product_pricing_info = {
            'marketplace_id': marketplace_id,
            'asin': asin,
            'price': {
                'landed_price': item['Product']['CompetitivePricing']['CompetitivePrices'][0]['Price']['LandedPrice'],
                'listing_price': item['Product']['CompetitivePricing']['CompetitivePrices'][0]['Price']['ListingPrice'],
                'shipping_price': item['Product']['CompetitivePricing']['CompetitivePrices'][0]['Price']['Shipping']
            },
            'pricing_message': 'Success'
            #'sales_rankings': item['Product']['SalesRankings']
        }
        return_dict[asin] = product_pricing_info
        
    return return_dict

def refactor_codes_and_info(codes: str, info: dict, return_dict: dict):
    """
    Args:
        codes (str): Marketplace Ids separated by comma
        info (dict): Returned from get_product_info_for_asins
        return_dict (dict): Runtime dict to be returned
    Returns:
        return_dict
    """
    for marketplace_id in codes.split(','):
        return_dict[marketplace_id] = {
            'asin': info['asin'],
            'name': "",
            'weight': {},
            'dimensions': {},
            'package_dimensions': {},
            'sales_ranks': {},
        }
        
        try:
            for name in info['name']:
                return_dict[name['marketplaceId']]['name'] = name['itemName']
            for weight in info['weight']:
                return_dict[weight['marketplace_id']]['weight'] = weight
            for dimension in info['dimensions']:
                return_dict[dimension['marketplace_id']]['dimensions'] = dimension
            for package_dimension in info['package_dimensions']:
                return_dict[package_dimension['marketplace_id']]['package_dimensions'] = package_dimension
            for sales_rank in info['sales_ranks']:
                return_dict[sales_rank['marketplaceId']]['sales_ranks'] = sales_rank
        except Exception as error:
            print(f'An error happened while refactoring codes and info for {info["asin"]}:', error)
    
    return return_dict
def categorize_marketplace_ids_by_region(marketplace_ids: str) -> tuple:
    """
    Args:
        marketplace_ids (list): Comma delimited string
    Returns:
        tuple: Size of 3 tuple (asia_codes, europe_codes, us_codes)
    """
    asia_codes = []
    europe_codes = []
    us_codes = []
    
    for marketplace_id in marketplace_ids.split(','):
        country_code = MARKETPLACE_ID_TO_COUNTRY_CODE[marketplace_id]
        if (country_code in ASIA_COUNTRY_CODES):
            asia_codes.append(marketplace_id)
        elif (country_code in EUROPE_COUNTRY_CODES):
            europe_codes.append(marketplace_id)
        elif (country_code in US_COUNTRY_CODES):
            us_codes.append(marketplace_id)
    
    comma_delimited_string_asia_codes = ','.join(asia_codes)
    comma_delimited_string_europe_codes = ','.join(europe_codes)
    comma_delimited_string_us_codes = ','.join(us_codes)
            
    return comma_delimited_string_asia_codes, comma_delimited_string_europe_codes, comma_delimited_string_us_codes

def get_catalog_item_info_by_credentials_and_marketplace(credentials: dict, marketplace, asin: str, marketplace_ids: str) -> dict:
    """
    Args:
        credentials (dict): Credentials required to retrieve information with amazon sp-api
        marketplace: Marketplace value (ex: Marketplaces.US) 
        asin (str): ASIN of the product
        marketplace_ids (str): Comma delimited string contains marketplace ids.
    Returns:
        dict: Contains required information with key-value pairs.
    """
    res = CatalogItems(credentials=credentials, marketplace=marketplace)
    
    def inner_func(marketplace_ids):
        return res.get_catalog_item(asin=asin,
                                    marketplaceIds=marketplace_ids,
                                    includedData='salesRanks,summaries,attributes').payload
    
    def try_until_end(func, marketplace_ids):
        while len(marketplace_ids) > 0:
            try:
                return func(marketplace_ids)
            except SellingApiNotFoundException as error:
                print(f'An error happened while getting catalog item info for {asin}:', error)
                print('\nTrying again with different marketplace ids...\n')
                marketplace_ids_as_list = marketplace_ids.split(',')
                marketplace_id_to_remove = error.message.replace('.', '').split(' ')[-1]
                marketplace_ids_as_list.remove(marketplace_id_to_remove)
                
                marketplace_ids = ','.join(marketplace_ids_as_list) if len(marketplace_ids_as_list) > 0 else ''
        raise Exception('No marketplace id is valid.')
    
    try:
        result = try_until_end(inner_func, marketplace_ids)
    except Exception as error:
        print(f'An error happened while getting catalog item info for {asin}:', error)
        return {
            'asin': asin,
            'name': 'Error',
            'weight': [],
            'dimensions': [],
            'package_dimensions': [],
            'sales_ranks': []
        }
    
    info = {
        'asin': asin, # (str)
        'name': result['summaries'], # (list)
        'weight': result['attributes']['item_package_weight'] if 'item_package_weight' in result['attributes'] else [], # (list) contains dicts ex:(unit=grams, value=60.0, marketplace_id=A39IBJ37TRP1C6)
        'dimensions': result['attributes']['item_dimensions'] if 'item_dimensions' in result['attributes'] else [], # (list) contains dicts ex:(width,length,height,marketplace_id)
        'package_dimensions': result['attributes']['item_package_dimensions'] if 'item_package_dimensions' in result['attributes'] else [], # (list) contains dicts ex:(width,length,height,marketplace_id)
        'sales_ranks': result['salesRanks'], # (list) contains dicts ex:(marketplace_id, ranks(list contains dicts))
    }
    return info

def find_product_details_by_asin(marketplace_ids: str, asin: str) -> dict:
    """
    Args:
        marketplace_ids (str): Comma delimited string
        asin (str): ASIN
    Returns:
        dict: Returns a dict of dictionaries contains required information.
    """
    return_dict = {}
    asia_codes, europe_codes, us_codes = categorize_marketplace_ids_by_region(marketplace_ids=marketplace_ids)
    
    if (len(asia_codes) != 0):
        creds, marketplace = get_credentials_and_marketplace_by_country(country_code='AU')
        info = get_catalog_item_info_by_credentials_and_marketplace(credentials=creds,
                                                                    marketplace=marketplace,
                                                                    asin=asin,
                                                                    marketplace_ids=asia_codes)
        
        # update return_dict
        return_dict = refactor_codes_and_info(codes=asia_codes, info=info, return_dict=return_dict)
    if (len(europe_codes) != 0):
        creds, marketplace = get_credentials_and_marketplace_by_country(country_code='DE')
        info = get_catalog_item_info_by_credentials_and_marketplace(credentials=creds,
                                                                    marketplace=marketplace,
                                                                    asin=asin,
                                                                    marketplace_ids=europe_codes)
        
        # update return_dict
        return_dict = refactor_codes_and_info(codes=europe_codes, info=info, return_dict=return_dict)
    if (len(us_codes) != 0):
        creds, marketplace = get_credentials_and_marketplace_by_country(country_code='US')
        info = get_catalog_item_info_by_credentials_and_marketplace(credentials=creds,
                                                                    marketplace=marketplace,
                                                                    asin=asin,
                                                                    marketplace_ids=us_codes)
        
        # update return_dict
        return_dict = refactor_codes_and_info(codes=us_codes, info=info, return_dict=return_dict)
        
    return return_dict

def get_sellers_info_by_asin_and_marketplace_id(asin: str, marketplace_id: str) -> dict:
    """
    Args:
        asin (str): ASIN of the product
        marketplace_id (str): Marketplace ID (ex: A39IBJ37TRP1C6)
    Returns:
        dict: Contains sellers related information.
    """
    country_code = MARKETPLACE_ID_TO_COUNTRY_CODE[marketplace_id]
    credentials, marketplace = get_credentials_and_marketplace_by_country(country_code)
    
    res = Products(credentials=credentials, marketplace=marketplace)
    
    try:
        result = res.get_item_offers(asin=asin, item_condition='New').payload
    except Exception as e:
        result = {'status': 'Error'}
    
    if (result['status'] == 'Success'):
        offers = result['Offers']
        fba_sellers_count = 0
        fbm_sellers_count = 0
        
        for offer in offers:
            fba_sellers_count += 1 if offer['IsFulfilledByAmazon'] else 0
            fbm_sellers_count += 1 if not offer['IsFulfilledByAmazon'] else 0
        info = {
            'asin': asin, # (str)
            'marketplace_id': marketplace_id, # (str)
            'total_offer_count': result['Summary']['TotalOfferCount'], # (int)
            'fba_sellers_count': fba_sellers_count, # (int)
            'fbm_sellers_count': fbm_sellers_count, # (int)
            'lowest_offer': result['Summary']['LowestPrices'][0], # (dict) keys=[condition,fulfillmentChannel,LandedPrice,ListingPrice,Shipping]
            'buybox_offer': result['Summary']['BuyBoxPrices'][0] if 'BuyBoxPrices' in result['Summary'] else {}, # (dict) keys=[condition,LandedPrice,ListingPrice,Shipping]
            'offers': offers, # (list contains dicts) keys=[Shipping,ListingPrice,ShippingTime,SellerFeedbackRating,PrimeInformation,SubCondition,SellerId,IsFeaturedMerchant,IsBuyBoxWinner,IsFulfilledByAmazon]
            'seller_info_message': 'Success'
        }
        return info
    
    # if result['status'] == 'Error'
    return {
        'asin': asin,
        'marketplace_id': marketplace_id,
        'total_offer_count': 0,
        'fba_sellers_count': 0,
        'fbm_sellers_count': 0,
        'lowest_offer': {},
        'buybox_offer': {},
        'offers': [],
        'sellers_info_message': 'No sellers info found.'
    }
    
def get_product_details_and_sellers_info_by_asin_and_marketplaces(asin: str, marketplace_ids: str) -> dict:
    """
    Args:
        asin (str): ASIN of the product
        marketplace_ids (str): Marketplace IDs delimited with comma (ex: A39IBJ37TRP1C6)
    Returns:
        dict: Contains product details and sellers related information. Keys are marketplace URLs.
    """
    marketplaces_ids_as_list = marketplace_ids.split(',')
    return_dict = {}
    
    product_details = find_product_details_by_asin(marketplace_ids=marketplace_ids, asin=asin)
    for marketplace_id in marketplaces_ids_as_list:
        sellers_info = get_sellers_info_by_asin_and_marketplace_id(asin=asin, marketplace_id=marketplace_id)
        marketplace_url = MARKETPLACE_ID_TO_MARKETPLACE_URL[marketplace_id]
        return_dict[marketplace_url] = {**product_details[marketplace_id], **sellers_info}
    
    return return_dict

def write_search_results_to_excel(result, base_currency='USD'):
    data = result['data']
    
    identifiers = result['identifiers_list']
    marketplaces_to_look_list = result['marketplaces_to_look_list']
    marketplace_to_sell = result['marketplace_to_sell']
    
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('Compare Marketplaces Search Results.xlsx')
    worksheet_own_currency = workbook.add_worksheet('Search Results') 
    worksheet_base_currency = workbook.add_worksheet('Search Results in {}'.format(base_currency))

    # Headers
    headers = ['ASIN'] + marketplaces_to_look_list + [marketplace_to_sell] + [
        'Best Seller Rank',
        'Height',
        'Length',
        'Width',
        'Weight',
        'Total Sellers Count',
        'FBA Sellers Count',
        'FBM Sellers Count',
        'Buy Box Seller'
    ]
    write_headers_to_excel(worksheet=worksheet_own_currency, headers=headers)
    write_headers_to_excel(worksheet=worksheet_base_currency, headers=headers)
    
    # Write data to excel
    row = 1
    for identifier in identifiers:
        worksheet_own_currency.write(row, 0, identifier)
        worksheet_base_currency.write(row, 0, identifier)
        if identifier not in data:
            continue
        
        # write pricing info
        inner_data = data[identifier]['data']
        for marketplace, values in inner_data.items():
            currency = values['listing_price']['CurrencyCode']
            amount = values['listing_price']['Amount']
            amount_base = x_to_y_currency_converter(values['listing_price']['CurrencyCode'], base_currency, values['listing_price']['Amount'])
            
            worksheet_own_currency.write(row,
                                         headers.index(marketplace),
                                         '{} {}'.format(amount, currency))
            worksheet_base_currency.write(row,
                                          headers.index(marketplace),
                                          '{} {}'.format(x_to_y_currency_converter(values['listing_price']['CurrencyCode'], 'USD', values['listing_price']['Amount']), base_currency))

        # write product details and sellers info
        column = len(marketplaces_to_look_list) + 2 # +2 because of ASIN and marketplace_to_sell columns
        
        # best seller rank
        if len(inner_data[marketplace_to_sell]['sales_ranks']) != 0:
            if len(inner_data[marketplace_to_sell]['sales_ranks']['ranks']) != 0:
                best_seller_rank = inner_data[marketplace_to_sell]['sales_ranks']['ranks'][0]['rank']
            else:
                best_seller_rank = ''
        else:
            best_seller_rank = ''
        
        # other product details
        height = '' if len(inner_data[marketplace_to_sell]['dimensions']) == 0 else '{} {}'.format(inner_data[marketplace_to_sell]['dimensions']['height']['value'], inner_data[marketplace_to_sell]['dimensions']['height']['unit'])
        length = '' if len(inner_data[marketplace_to_sell]['dimensions']) == 0 else '{} {}'.format(inner_data[marketplace_to_sell]['dimensions']['length']['value'], inner_data[marketplace_to_sell]['dimensions']['length']['unit'])
        width = '' if len(inner_data[marketplace_to_sell]['dimensions']) == 0 else '{} {}'.format(inner_data[marketplace_to_sell]['dimensions']['width']['value'], inner_data[marketplace_to_sell]['dimensions']['width']['unit'])
        weight = '' if len(inner_data[marketplace_to_sell]['weight']) == 0 else '{} {}'.format(inner_data[marketplace_to_sell]['weight']['value'], inner_data[marketplace_to_sell]['weight']['unit'])
        total_sellers_count = inner_data[marketplace_to_sell]['total_offer_count']
        fba_sellers_count = inner_data[marketplace_to_sell]['fba_sellers_count']
        fbm_sellers_count = inner_data[marketplace_to_sell]['fbm_sellers_count']
        
        buybox_seller = ''
        for offer in inner_data[marketplace_to_sell]['offers']:
            if offer['IsBuyBoxWinner']:
                buybox_seller = offer['SellerId']
                break
        
        additional_write_data = [best_seller_rank, height, length, width, weight, total_sellers_count, fba_sellers_count, fbm_sellers_count, buybox_seller]
        
        for value in additional_write_data:
            worksheet_own_currency.write(row, column, value)
            worksheet_base_currency.write(row, column, value)
            column += 1
        
        row += 1
    workbook.close()
    
def start_compare_search(marketplaces_to_look_for: list, marketplace_to_sell: str, identifiers: list, error_label):
    """_summary_
    Args:
        marketplaces_to_look_for (list): Example: ['amazon.com', 'amazon.co.uk' ...]
        marketplace_to_sell (str): Example: 'amazon.com'
        asins_list (list): List contains ASINs
        error_label (tk.Label): Label to show errors
    """

    ALL_MARKETPLACES = marketplaces_to_look_for + [marketplace_to_sell] # marketplace_to_sell is also a marketplace to look for
    error_label.config(text="")
    
    if (len(marketplaces_to_look_for) == 0 or len(identifiers) == 0):
        error_label.config(text="Please choose marketplaces and identifiers.")
        return
    
    search_id = generate_unique_id()
    username = EXAMPLE_USERNAME
    
    create_search = create_compare_search(search_id=search_id,
                                          username=username,
                                          identifier_type='ASIN',
                                          identifiers_list=identifiers,
                                          marketplaces_to_look_list=marketplaces_to_look_for,
                                          marketplace_to_sell=marketplace_to_sell)
    
    if (create_search['status'] == 'error'):
        error_label.config(text="Error while creating search.")
        return
    
    # divide identifiers into chunks (Max 20 ASINs per request allowed by Amazon SP-API)
    DIVIDE_SIZE = 20
    identifiers_divided = break_list_into_chunks(identifiers, DIVIDE_SIZE)
    
    change_search_status_to_in_progress(search_id=search_id)
    error_label.config(text="Search is in progress...")
    
    counter = 0
    for identifiers_chunk in identifiers_divided:
        error_label.config(text="Search is in progress... ({}%)".format(int( (counter / len(identifiers_divided)) * 100 )))
        sub_result = {}
        for marketplace in ALL_MARKETPLACES:
            # get pricing info for asins
            pricing_info = get_pricing_info_for_asins(marketplace_id=MARKETPLACE_URL_TO_MARKETPLACE_ID[marketplace],
                                                      asins_list=identifiers_chunk)
            # add pricing info to sub_result
            for asin in pricing_info:
                try:
                    if asin in sub_result:
                        sub_result[asin][marketplace] = pricing_info[asin]['price']
                    else:
                        sub_result[asin] = {marketplace: pricing_info[asin]['price']}
                except Exception as e:
                    print("Exception:", e)
        
        # get product details and sellers info for asins
        for asin in sub_result:
            product_details_and_sellers_info = get_product_details_and_sellers_info_by_asin_and_marketplaces(asin=asin,
                                                                                                         marketplace_ids=MARKETPLACE_URL_TO_MARKETPLACE_ID[marketplace_to_sell])
            
            for marketplace, values in product_details_and_sellers_info.items():
                if marketplace in sub_result[asin]:
                    sub_result[asin][marketplace] = {**sub_result[asin][marketplace], **values}
            
            print('Got product details and sellers info for asin:', asin)

        # add sub_result to database
        create_result = create_compare_result_in_bulk(
            search_id=search_id,
            identifier_type='ASIN',
            sub_result=sub_result
        )
        print(create_result)
        counter += 1
    
    change_search_status_to_finished(search_id=search_id)
    error_label.config(text="Search is done.")

    # write results to excel
    error_label.config(text="Writing results to excel...")
    data = get_compare_results_by_search_id(search_id=search_id)
    if (data['status'] == 'success'):
        write_search_results_to_excel(data['result'])
    else:
        error_label.config(text="An error occured while writing results to excel.")
    
    error_label.config(text="Done.")