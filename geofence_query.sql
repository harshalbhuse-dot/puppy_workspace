CREATE OR REPLACE TABLE `wmt-driver-insights.Chirag_dx.geofence_delivered_distance_1yr` AS 
WITH all_final AS (
  SELECT 
    sales_order_num, 
    po_num,
  FROM `wmt-edw-sandbox.LMD_DA.SPARK_DELIVERY_DS_ALL_FINAL`
  WHERE Slot_DT BETWEEN "2025-02-10" AND "2026-02-09"
  AND UPPER(first_assgn_carrier_nm) = "SPARK"
  AND (
    (UPPER(fulfilment_type) LIKE 'SCHE%' AND UPPER(picker_type_nm) = 'ASSOCIATE' AND UPPER(REC_SRC) <> 'DAAS' AND UPPER(client) = 'WALMART' AND UPPER(carrier_org_nm) = 'SPARK')
    OR (UPPER(fulfilment_type) LIKE 'SCHE%' AND UPPER(picker_type_nm) = 'SHOPPER' AND UPPER(REC_SRC) <> 'DAAS' AND UPPER(client) = 'WALMART' AND UPPER(carrier_org_nm) = 'SPARK')
    OR (UPPER(fulfilment_type) LIKE '%EVERGREEN%' AND UPPER(picker_type_nm) = 'SHOPPER' AND UPPER(REC_SRC) <> 'DAAS' AND UPPER(client) = 'WALMART' AND UPPER(carrier_org_nm) = 'SPARK')
    OR (UPPER(fulfilment_type) LIKE '%EXPRESS%' AND UPPER(picker_type_nm) = 'SHOPPER' AND UPPER(REC_SRC) <> 'DAAS' AND UPPER(client) = 'WALMART' AND UPPER(carrier_org_nm) = 'SPARK')
    OR (UPPER(fulfilment_type) LIKE '%UNSCH%' AND UPPER(picker_type_nm) <> 'SHOPPER' AND UPPER(REC_SRC) <> 'DAAS' AND UPPER(client) = 'WALMART' AND UPPER(carrier_org_nm) = 'SPARK')
  )
  AND CARRIER_DLVR_TS_TZ IS NOT NULL
  GROUP BY 1,2
),
arrv_loc AS (
  SELECT 
    SALES_ORDER_NBR, 
    PO_NBR,
    IF(REGEXP_CONTAINS(CAST(DRVR_DROPOFF_LOC_LAT_NBR AS STRING), r'[0-9]+\.[0-9]{5,6}') IS TRUE, DRVR_DROPOFF_LOC_LAT_NBR, NULL) AS arrival_lat,
    IF(REGEXP_CONTAINS(CAST(DRVR_DROPOFF_LOC_LONG_NBR AS STRING), r'[0-9]+\.[0-9]{5,6}') IS TRUE, DRVR_DROPOFF_LOC_LONG_NBR, NULL) AS arrival_long,
  FROM (
    SELECT 
      SALES_ORDER_NBR, 
      PO_NBR, 
      DRVR_DROPOFF_LOC_LAT_NBR, 
      DRVR_DROPOFF_LOC_LONG_NBR,
      ROW_NUMBER() OVER (PARTITION BY SALES_ORDER_NBR, PO_NBR ORDER BY CREATE_TS DESC) AS row_num_desc
    FROM `wmt-edw-prod.WW_SUPPLY_CHAIN_DL_VM.DLVR_LAST_MI_DTL`
    WHERE DRVR_DROPOFF_LOC_LAT_NBR IS NOT NULL
    AND PO_NBR IN (SELECT po_num FROM all_final)
  )
  WHERE row_num_desc = 1
),
cust_loc AS (
  SELECT * FROM (
    SELECT DISTINCT 
      SRC_SALES_ORDER_NBR, 
      PO_NUM,
      IF(REGEXP_CONTAINS(CAST(CUST_RQ_DLVR_LAT_DGR_QTY AS STRING), r'[0-9]+\.[0-9]{5,6}') IS TRUE, CUST_RQ_DLVR_LAT_DGR_QTY, NULL) AS CUST_RQ_DLVR_LAT_NBR,
      IF(REGEXP_CONTAINS(CAST(CUST_RQ_DLVR_LONG_DGR_QTY AS STRING), r'[0-9]+\.[0-9]{5,6}') IS TRUE, CUST_RQ_DLVR_LONG_DGR_QTY, NULL) AS CUST_RQ_DLVR_LONG_NBR,
      IF(REGEXP_CONTAINS(CAST(PKG_DROPOFF_LAT_DGR_QTY AS STRING),r'[0-9]+\.[0-9]{5,6}') IS TRUE, PKG_DROPOFF_LAT_DGR_QTY, NULL) AS Delivered_lat,
      IF(REGEXP_CONTAINS(CAST(PKG_DROPOFF_LONG_DGR_QTY AS STRING), r'[0-9]+\.[0-9]{5,6}') IS TRUE, PKG_DROPOFF_LONG_DGR_QTY, NULL) AS Delivered_long,
      ROW_NUMBER() OVER (PARTITION BY po_num ORDER BY CREATE_TS DESC) AS row_num_desc,
    FROM `wmt-edw-prod.WW_SUPPLY_CHAIN_DL_SECURE.LAST_MI_DLVR_ORDER_ADDR_DTL`
    WHERE CUST_RQ_DLVR_LAT_DGR_QTY IS NOT NULL
    AND PO_NUM IN (SELECT po_num FROM all_final)
  )
  WHERE row_num_desc = 1
),
addr AS (
  SELECT * FROM (
    SELECT DISTINCT 
      SRC_SALES_ORDER_NBR, 
      po_num,
      CUST_RQ_ADDR_TYPE_NM,
      CUST_RQ_ADDR_SRC_NM,
      CUST_RQ_ADDR_NEED_ACES_CD_OPT_NM,
      ROW_NUMBER() OVER (PARTITION BY po_num ORDER BY CREATE_TS DESC) AS row_num_desc,
    FROM `wmt-edw-prod.WW_SUPPLY_CHAIN_DL_SECURE.LAST_MI_DLVR_ORDER_ADDR_DTL`
    WHERE PO_NUM IN (SELECT po_num FROM all_final)
  )
  WHERE row_num_desc = 1
)
SELECT 
  all_final.sales_order_num,
  all_final.po_num,
  arrv_loc.arrival_lat,
  arrv_loc.arrival_long,
  cust_loc.CUST_RQ_DLVR_LAT_NBR,
  cust_loc.CUST_RQ_DLVR_LONG_NBR,
  ST_DISTANCE(ST_GEOGPOINT(arrival_long, arrival_lat), ST_GEOGPOINT(CUST_RQ_DLVR_LONG_NBR, CUST_RQ_DLVR_LAT_NBR)) AS ARRVL_DIST_METER,
  ST_DISTANCE(ST_GEOGPOINT(arrival_long, arrival_lat), ST_GEOGPOINT(CUST_RQ_DLVR_LONG_NBR, CUST_RQ_DLVR_LAT_NBR)) / 1609.34 AS ARRVL_DIST_MILE,
  ST_DISTANCE(ST_GEOGPOINT(Delivered_long, Delivered_lat), ST_GEOGPOINT(CUST_RQ_DLVR_LONG_NBR, CUST_RQ_DLVR_LAT_NBR)) AS DLVRD_DIST_METER,
  ST_DISTANCE(ST_GEOGPOINT(Delivered_long, Delivered_lat), ST_GEOGPOINT(CUST_RQ_DLVR_LONG_NBR, CUST_RQ_DLVR_LAT_NBR)) / 1609.34 AS DLVRD_DIST_MILE,
  addr.CUST_RQ_ADDR_TYPE_NM,
  addr.CUST_RQ_ADDR_SRC_NM,
  addr.CUST_RQ_ADDR_NEED_ACES_CD_OPT_NM,
FROM all_final
LEFT JOIN arrv_loc ON arrv_loc.SALES_ORDER_NBR = all_final.sales_order_num AND arrv_loc.PO_NBR = all_final.po_num
LEFT JOIN cust_loc ON cust_loc.SRC_SALES_ORDER_NBR = all_final.sales_order_num AND cust_loc.po_num = all_final.po_num
LEFT JOIN addr ON addr.src_sales_order_nbr = all_final.sales_order_num AND addr.po_num = all_final.po_num
GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13
