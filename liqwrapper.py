import requests

class ApiWrapper:
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url

        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "sec-gpc": "1",
            "site_subdomain": "liquidationmaxinc.hibid.com"
        }

        if auth_token:
            self.headers["authorization"] = f"Bearer {auth_token}"

    def fetch_graphql(self, query: str, variables: dict, operation_name: str):

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={
                    "operationName": operation_name,  # Extracts operation name
                    "variables": variables,
                    "query": query
                },
            )

            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Fetch Error: {e}")
            raise Exception(f"Failed to fetch data: {e}")

    def bid_on_lot(self, lot_id: int, bid_amount: float, re_confirmed: bool):
        query = """
            mutation LotBid($lotId: Int!, $bidAmount: Decimal!, $reConfirmed: Boolean!) {
                bid(input: { lotId: $lotId, bidAmount: $bidAmount, reConfirmed: $reConfirmed }) {
                    __typename
                    ... on BidResultType {
                        bidStatus
                        suggestedBid
                        bidMessage
                        lot {
                            ...lotFull
                            __typename
                        }
                        __typename
                    }
                    ...InvalidInputErrors
                }
            }

            fragment lotFull on Lot {
                id
                description
            }

            fragment InvalidInputErrors on InvalidInputError {
                messages
                errors {
                    fieldName
                    messages
                }
            }
        """

        try:
            data = self.fetch_graphql(query, {"lotId": lot_id, "bidAmount": bid_amount, "reConfirmed": re_confirmed}, "LotBid")

            if 'bid' in data['data']:
                return data['data']['bid']
            elif 'InvalidInputErrors' in data['data']:
                return data['data']['InvalidInputErrors']
            else:
                return None
        except Exception as e:
            print(f"Error bidding on lot: {e}")
            return None

    def get_current_bids(self):
        query = """
            query CurrentBidsSearch(
                $isArchived: Boolean = false, 
                $groupByAuction: Boolean = true, 
                $auctionSortDirection: SortDirection = ASC, 
                $hideClosedLots: Boolean = false, 
                $pageNumber: Int!, 
                $pageLength: Int!, 
                $auctionId: Int = null, 
                $buyerLotStatusGroup: BuyerLotStatusGroup = null, 
                $sortOrder: BuyerEventItemSortOrder = null, 
                $monthRange: AltBidPastBidsRange = null, 
                $sortDirection: SortDirection = DESC
            ) {
                currentBids(
                    input: {
                        isArchived: $isArchived, 
                        groupByAuction: $groupByAuction, 
                        auctionSortDirection: $auctionSortDirection, 
                        hideClosedLots: $hideClosedLots, 
                        auctionId: $auctionId, 
                        buyerLotStatusGroup: $buyerLotStatusGroup, 
                        sortOrder: $sortOrder, 
                        monthRange: $monthRange
                    }, 
                    pageNumber: $pageNumber, 
                    pageLength: $pageLength, 
                    sortDirection: $sortDirection
                ) {
                    auctions {
                        ...auction
                        __typename
                    }
                    pagedResults {
                        pageLength
                        pageNumber
                        totalCount
                        filteredCount
                        results {
                            ...lotFull
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            }

            
fragment auction on Auction {
  id
  altBiddingUrl
  altBiddingUrlCaption
  amexAccepted
  discoverAccepted
  mastercardAccepted
  visaAccepted
  regType
  holdAmount
  auctioneer {
    ...auctioneer
    __typename
  }
  auctionNotice
  auctionOptions {
    bidding
    altBidding
    catalog
    liveCatalog
    shippingType
    preview
    registration
    webcast
    useLotNumber
    useSaleOrder
    __typename
  }
  auctionState {
    auctionStatus
    bidCardNumber
    isRegistered
    openLotCount
    timeToOpen
    __typename
  }
  bidAmountType
  biddingNotice
  bidIncrements {
    minBidIncrement
    upToAmount
    __typename
  }
  bidOpenDateTime
  bidCloseDateTime
  bidType
  buyerPremium
  buyerPremiumRate
  checkoutDateInfo
  previewDateInfo
  currencyAbbreviation
  description
  eventAddress
  eventCity
  eventDateBegin
  eventDateEnd
  eventDateInfo
  eventName
  eventState
  eventZip
  featuredPicture {
    description
    fullSizeLocation
    height
    hdThumbnailLocation
    thumbnailLocation
    width
    __typename
  }
  links {
    description
    id
    type
    url
    videoId
    __typename
  }
  lotCount
  showBuyerPremium
  audioVideoChatInfo {
    aVCEnabled
    blockChat
    __typename
  }
  shippingAndPickupInfo
  paymentInfo
  hidden
  sourceType
  distanceMiles
  __typename
}

fragment auctioneer on Auctioneer {
  address
  bidIncrementDisclaimer
  buyerRegNotesCaption
  city
  countryId
  country
  cRMID
  email
  fax
  id
  internetAddress
  missingThumbnail
  name
  noMinimumCaption
  phone
  state
  postalCode
  __typename
}

fragment lotFull on Lot {
  auction {
    ...auction
    __typename
  }
  ...lotOnly
  __typename
}

fragment lotOnly on Lot {
  bidAmount
  bidList
  bidQuantity
  description
  estimate
  featuredPicture {
    description
    fullSizeLocation
    height
    hdThumbnailLocation
    thumbnailLocation
    width
    __typename
  }
  forceLiveCatalog
  fr8StarUrl
  hideLeadWithDescription
  id
  itemId
  lead
  links {
    description
    id
    type
    url
    videoId
    __typename
  }
  linkTypes
  lotNavigator {
    lotCount
    lotPosition
    nextId
    previousId
    __typename
  }
  lotNumber
  lotState {
    ...lotState
    __typename
  }
  pictureCount
  pictures {
    description
    fullSizeLocation
    height
    hdThumbnailLocation
    thumbnailLocation
    width
    __typename
  }
  quantity
  ringNumber
  rv
  category {
    baseCategoryId
    categoryName
    description
    fullCategory
    header
    id
    parentCategoryId
    uRLPath
    __typename
  }
  shippingOffered
  simulcastStatus
  site {
    domain
    fr8StarUrl
    isDomainRequest
    isExtraWWWRequest
    siteType
    subdomain
    __typename
  }
  saleOrder
  __typename
}

fragment lotState on LotState {
  bidCount
  biddingExtended
  bidMax
  bidMaxTotal
  buyerBidStatus
  buyerHighBid
  buyerHighBidTotal
  buyNow
  choiceType
  highBid
  highBuyerId
  isArchived
  isClosed
  isHidden
  isLive
  isNotYetLive
  isOnLiveCatalog
  isPosted
  isPublicHidden
  isRegistered
  isWatching
  linkedSoftClose
  mayHaveWonStatus
  minBid
  priceRealized
  priceRealizedMessage
  priceRealizedPerEach
  productStatus
  productUrl
  quantitySold
  reserveSatisfied
  sealed
  showBidStatus
  showReserveStatus
  softCloseMinutes
  softCloseSeconds
  status
  timeLeft
  timeLeftLead
  timeLeftSeconds
  timeLeftTitle
  timeLeftWithLimboSeconds
  timeLeftWithLimboSeconds
  watchNotes
  __typename
}
        """

        variables = {
            "isArchived": False,
            "groupByAuction": True,
            "auctionSortDirection": "ASC",
            "hideClosedLots": False,
            "auctionId": 0,
            "buyerLotStatusGroup": "ALL",
            "sortOrder": "SALES_ORDER",
            "monthRange": "THREE_MONTHS",
            "sortDirection": "ASC",
            "pageNumber": 1,
            "pageLength": 100
        }

        try:
            data = self.fetch_graphql(query, variables, "CurrentBidsSearch")

            if 'currentBids' in data['data']:
                return data['data']['currentBids']['pagedResults']['results']
            else:
                return None
        except Exception as e:
            print(f"Error fetching current bids: {e}")
            return None
    def search_auction_products(self, auction_id, category =-1, page_number=1, page_length=100, search_text=None):
        body = {
        "operationName": "LotSearch",
        "variables": {
            "auctionId": auction_id,
            "category": category,
            "searchText": search_text,
            "zip": "",
            "miles": 50,
            "shippingOffered": False,
            "countryName": "",
            "status": "ALL",
            "sortOrder": "LOT_NUMBER",
            "filter": "ALL",
            "isArchive": False,
            "countAsView": True,
            "hideGoogle": False,
            "pageNumber": page_number,
            "pageLength": page_length
        },
        "query": """query LotSearch($auctionId: Int = null, $pageNumber: Int!, $pageLength: Int!, $category: CategoryId = null, $searchText: String = null, $zip: String = null, $miles: Int = null, $shippingOffered: Boolean = false, $countryName: String = null, $status: AuctionLotStatus = null, $sortOrder: EventItemSortOrder = null, $filter: AuctionLotFilter = null, $isArchive: Boolean = false, $dateStart: DateTime, $dateEnd: DateTime, $countAsView: Boolean = true, $hideGoogle: Boolean = false) {
  lotSearch(
    input: {auctionId: $auctionId, category: $category, searchText: $searchText, zip: $zip, miles: $miles, shippingOffered: $shippingOffered, countryName: $countryName, status: $status, sortOrder: $sortOrder, filter: $filter, isArchive: $isArchive, dateStart: $dateStart, dateEnd: $dateEnd, countAsView: $countAsView, hideGoogle: $hideGoogle}
    pageNumber: $pageNumber
    pageLength: $pageLength
    sortDirection: DESC
  ) {
    pagedResults {
      pageLength
      pageNumber
      totalCount
      filteredCount
      results {
        auction {
          ...auctionMinimum
          __typename
        }
        bidAmount
        bidList
        bidQuantity
        description
        estimate
        featuredPicture {
          description
          fullSizeLocation
          height
          hdThumbnailLocation
          thumbnailLocation
          width
          __typename
        }
        forceLiveCatalog
        fr8StarUrl
        hideLeadWithDescription
        id
        itemId
        lead
        links {
          description
          id
          type
          url
          videoId
          __typename
        }
        linkTypes
        lotNumber
        lotState {
          bidCount
          biddingExtended
          bidMax
          bidMaxTotal
          buyerBidStatus
          buyerHighBid
          buyerHighBidTotal
          buyNow
          choiceType
          highBid
          highBuyerId
          isArchived
          isClosed
          isHidden
          isLive
          isNotYetLive
          isOnLiveCatalog
          isPosted
          isPublicHidden
          isRegistered
          isWatching
          linkedSoftClose
          mayHaveWonStatus
          minBid
          priceRealized
          priceRealizedMessage
          priceRealizedPerEach
          productStatus
          productUrl
          quantitySold
          reserveSatisfied
          sealed
          showBidStatus
          showReserveStatus
          softCloseMinutes
          softCloseSeconds
          status
          timeLeft
          timeLeftLead
          timeLeftSeconds
          timeLeftTitle
          timeLeftWithLimboSeconds
          timeLeftWithLimboSeconds
          watchNotes
          __typename
        }
        pictureCount
        quantity
        ringNumber
        rv
        shippingOffered
        simulcastStatus
        site {
          domain
          fr8StarUrl
          isDomainRequest
          isExtraWWWRequest
          siteType
          subdomain
          __typename
        }
        distanceMiles
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment auctionMinimum on Auction {
  id
  altBiddingUrl
  altBiddingUrlCaption
  amexAccepted
  discoverAccepted
  mastercardAccepted
  visaAccepted
  regType
  holdAmount
  auctioneer {
    ...auctioneer
    __typename
  }
  auctionOptions {
    bidding
    altBidding
    catalog
    liveCatalog
    shippingType
    preview
    registration
    webcast
    useLotNumber
    useSaleOrder
    __typename
  }
  auctionState {
    auctionStatus
    bidCardNumber
    isRegistered
    openLotCount
    timeToOpen
    __typename
  }
  bidAmountType
  bidIncrements {
    minBidIncrement
    upToAmount
    __typename
  }
  bidOpenDateTime
  bidCloseDateTime
  bidType
  buyerPremium
  buyerPremiumRate
  checkoutDateInfo
  previewDateInfo
  currencyAbbreviation
  description
  eventAddress
  eventCity
  eventDateBegin
  eventDateEnd
  eventDateInfo
  eventName
  eventState
  eventZip
  featuredPicture {
    description
    fullSizeLocation
    height
    hdThumbnailLocation
    thumbnailLocation
    width
    __typename
  }
  links {
    description
    id
    type
    url
    videoId
    __typename
  }
  lotCount
  showBuyerPremium
  audioVideoChatInfo {
    aVCEnabled
    blockChat
    __typename
  }
  hidden
  sourceType
  distanceMiles
  __typename
}

fragment auctioneer on Auctioneer {
  address
  bidIncrementDisclaimer
  buyerRegNotesCaption
  city
  countryId
  country
  cRMID
  email
  fax
  id
  internetAddress
  missingThumbnail
  name
  noMinimumCaption
  phone
  state
  postalCode
  __typename
}"""
    }
        results = self.fetch_graphql(body["query"], body["variables"], "LotSearch")
        return results["data"]["lotSearch"]

    def iter_auction_products(self, auction_id, category=-1, page_length=100):
        page_number = 1
        while True:
            data = self.search_auction_products(auction_id, category=category, page_number=page_number, page_length=page_length)
            results = data['pagedResults']['results']
            
            if not results:
                break
            
            for result in results:
                yield result
            
            total_count = data['pagedResults']['totalCount']
            filtered_count = data['pagedResults']['filteredCount']
            print(total_count, filtered_count)
            if filtered_count <= page_number * page_length:
                break
            
            page_number += 1