# Includes brands to track.
#
# name:               Brand name. Used to build seen_listings filenames.
#
# channel_id:         Discord channel ID to post this brand's listings to.
#
# grailed_query:        Optional Grailed keyword search (can be combined with IDs).
# grailed_designer_ids: Optional list of Grailed designer IDs. Grailed independently
#                      searches by keyword AND by these IDs, then merges results.
# mercari_brand_ids:    Optional list of Mercari brand IDs. Searched by ID if nonempty.
# mercari_query:        Keyword to search when no Mercari brand IDs are available.
#                       Defaults to the brand's name if omitted.
#
# To enable the new options, add the following fields to a brand entry:
#   "grailed_designer_ids": [1234],  # Replace [] with the real Grailed ID(s)
#   "mercari_brand_ids": [],          # Empty for an unregistered brand
#   "mercari_query": "brand keyword", # Used only when ID list is empty

BRANDS = [
  {
    "name": "14th Addiction",
    "channel_id": 1547507936488718419,
    "grailed_query": "14th addiction",
    # 14th Addiction
    "grailed_designer_ids": [39645],
    # 14th Addiction, CATORCE
    "mercari_brand_ids": [15224, 11446]
  },
  {
    "name": "Ann Demeulemeester",
    "channel_id": 1547508157620690954,
    "grailed_query": "ann demeulemeester",
    # Ann Demeulemeester
    "grailed_designer_ids": [261],
    # Ann Demeulemeester
    "mercari_brand_ids": [198]
  },
  {
    "name": "Attachment",
    "channel_id": 1547510436239249478,
    "grailed_query": "attachment",
    # Attachment, Kazuyuki Kumagai Attachment
    "grailed_designer_ids": [299, 35061],
    # ATTACHMENT, KAZUYUKI KUMAGAI, KAZUYUKI KUMAGAI ATTACHMENT
    "mercari_brand_ids": [91, 4165, 5883]
  },
  {
    "name": "Isamu Katayama Backlash",
    "channel_id": 1547489159390953544,
    "grailed_query": "isamu katayama backlash",
    # Isamu Katayama Backlash
    "grailed_designer_ids": [3276],
    # ISAMUKATAYAMA BACKLASH, ISAMU KATAYAMA, BACKLASH
    "mercari_brand_ids": [5808, 15421, 11072]
  },
  {
    "name": "Balenciaga",
    "channel_id": 1557450920793608242,
    "grailed_query": "balenciaga",
    # Balenciaga
    "grailed_designer_ids": [136],
    # BALENCIAGA
    "mercari_brand_ids": [954]
  },
  {
    "name": "Beauty Beast",
    "channel_id": 1547510041182212176,
    "grailed_query": "beauty beast",
    # Beauty Beast
    "grailed_designer_ids": [32392],
    # beauty:beast
    "mercari_brand_ids": [5186]
  },
  {
    "name": "Blackmeans",
    "channel_id": 1554559203757002813,
    "grailed_query": "blackmeans",
    # Blackmeans
    "grailed_designer_ids": [2263],
    # blackmeans
    "mercari_brand_ids": [7664]
  },
  {
    "name": "Deal Design",
    "channel_id": 1563485442785939566,
    "grailed_query": "deal design",
    # Deal Design
    "grailed_designer_ids": [41615],
    # DEAL DESIGN
    "mercari_brand_ids": [5419]
  },
  {
    "name": "Dior Homme",
    "channel_id": 1548094224396714085,
    "grailed_query": "dior homme",
    # Dior, Hedi Slimane
    "grailed_designer_ids": [35, 5531],
    # Dior Homme
    "mercari_brand_ids": [7331]
  },
  {
    "name": "GOA",
    "channel_id": 1547509823250370611,
    "grailed_query": "goa",
    # GOA
    "grailed_designer_ids": [41653],
    # goa
    "mercari_brand_ids": [542]
  },
  {
    "name": "Guidi",
    "channel_id": 1547023147365306510,
    "grailed_query": "guidi",
    "grailed_designer_ids": [18],
    # GUIDI
    "mercari_brand_ids": [5699]
  },
  {
    "name": "Hysteric Glamour",
    "channel_id": 1547507009677565992,
    "grailed_query": "hysteric glamour",
    # Hysteric Glamour
    "grailed_designer_ids": [3442],
    # Hysteric Glamour, HYSTERICS, Thee Hysteric XXX
    "mercari_brand_ids": [982, 5777, 6710]
  },
  {
    "name": "IF SIX WAS NINE",
    "channel_id": 1547507909871673385,
    "grailed_query": "if six was nine",
    # If Six Was Nine
    "grailed_designer_ids": [9612],
    # IF SIX WAS NINE
    "mercari_brand_ids": [3899]
  },
  {
    "name": "JULIUS",
    "channel_id": 1547506662091259934,
    "grailed_query": "julius",
    # Julius
    "grailed_designer_ids": [1],
    # JULIUS, MA_JULIUS
    "mercari_brand_ids": [4059, 24353]
  },
  {
    "name": "KLASICA",
    "channel_id": 1547650243447750656,
    "grailed_query": "klasica",
    # KLASICA
    "grailed_designer_ids": [33958],
    # KLASICA
    "mercari_brand_ids": [28075]
  },
  {
    "name": "KMRii",
    "channel_id": 1547505000970850406,
    "grailed_query": "kmrii",
    "grailed_designer_ids": [32317],
    # KMRii
    "mercari_brand_ids": [12820]
  },
  {
    "name": "Koji Kuga",
    "channel_id": 1547510078645608478,
    "grailed_query": "koji kuga",
    "grailed_designer_ids": [41790],
    "mercari_query": "koji kuga"
  },
  {
    "name": "LAD MUSICIAN",
    "channel_id": 1547510671506276403,
    "grailed_query": "lad musician",
    "grailed_designer_ids": [],
    # LAD MUSICIAN
    "mercari_brand_ids": [1269]
  },
  {
    "name": "LGB",
    "channel_id": 1547509456319938680,
    "grailed_query": "lgb",
    "grailed_designer_ids": [64],
    # LGB, L.G.B.
    "mercari_brand_ids": [4371, 3848]  
  },
  {
  "name": "Loud Style Design",
  "channel_id": 1563486105376923738,
  "grailed_query": "loud style design",
  "grailed_designer_ids": [],
  # Loud Style Design
  "mercari_brand_ids": [8296]  
  },
  {
    "name": "Maurizio Amadei",
    "channel_id": 1547509730203668571,
    "grailed_query": "maurizio amadei",
    # Ma+
    "grailed_designer_ids": [146],
    # m.a+
    "mercari_brand_ids": [7617]
  },
  {
    "name": "Number Nine",
    "channel_id": 1547509524766658581,
    "grailed_query": "number nine",
    # Number (N)ine
    "grailed_designer_ids": [799],
    # NUMBER (N)INE
    "mercari_brand_ids": [873]  
  },
  {
    "name": "Obelisk",
    "channel_id": 1547510480522711080,
    "grailed_query": "obelisk",
    # Obelisk
    "grailed_designer_ids": [40742],
    # Obelisk
    "mercari_brand_ids": [393]  
  },
  {
    "name": "Rick Owens",
    "channel_id": 1547508377888890920,
    "grailed_query": "rick owens",
    # Rick Owens, Rick Owens Drkshdw, Rick Owens Lilies
    "grailed_designer_ids": [32, 583, 37490],
    # Rick Owens, Rick Owens DRKSHDW, DRKSHDW
    "mercari_brand_ids": [1295, 7476, 5471]  
  },
  {
    "name": "Roen",
    "channel_id": 1547510277422059562,
    "grailed_query": "roen",
    # Roen
    "grailed_designer_ids": [7553],
    # Roen, roen jeans
    "mercari_brand_ids": [1365, 53888]  
  },
  {
    "name": "Saint Laurent",
    "channel_id": 1547510230794117251,
    "grailed_query": "saint laurent",
    # Saint Laurent Paris
    "grailed_designer_ids": [1621],
    # SAINT LAURENT PARIS, Saint Laurent, Yves Saint Laurent
    "mercari_brand_ids": [17163, 606, 219]  
  },
  {
    "name": "Tornado Mart",
    "channel_id": 1547509903181226045,
    "grailed_query": "tornado mart",
    # Tornado Mart
    "grailed_designer_ids": [31996],
    # TORNADO MART
    "mercari_brand_ids": [1720]  
  },
  {
    "name": "Vetements",
    "channel_id": 1557450887058825277,
    "grailed_query": "vetements",
    # Vetements
    "grailed_designer_ids": [9910],
    # VETEMENTS
    "mercari_brand_ids": [7549]  
  },
  {
    "name": "The Viridi Anne",
    "channel_id": 1547507836928524349,
    "grailed_query": "viridi anne",
    # The Viridi-anne
    "grailed_designer_ids": [100],
    # The Viridi-anne
    "mercari_brand_ids": [6707]  
  },
  {
    "name": "Yohji",
    "channel_id": 1547506894451515392,
    "grailed_query": "yohji",
    # Yohji Yamamoto, Y-3, Ground Y, Y's for Men, Y's
    "grailed_designer_ids": [288, 178, 36680, 3408, 38051],
    # Yohji Yamamoto, Yohji Yamamoto POUR HOMME, Y-3, REGULATION Yohji Yamamoto, Yohji Yamamoto +Noir, discord Yohji Yamamoto, PROTOTYPE BY YOHJI YAMAMOTO
    "mercari_brand_ids": [1253, 51232, 1980, 53500, 51233, 16258, 46010]  
  }
]