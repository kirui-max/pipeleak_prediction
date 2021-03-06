DROP MATERIALIZED VIEW IF EXISTS ws.v_ai_leak_arc_aux CASCADE;

CREATE MATERIALIZED VIEW ws.v_ai_leak_arc_aux AS
	SELECT
		row_number() OVER (order by arc_id) as id,
		arc_id::bigint,
		minsector_id::bigint,
		presszone_id::bigint,
		CASE
			WHEN broken = TRUE THEN ((leak_date - builtdate) / 365.0)::numeric
			ELSE ((now()::DATE - builtdate) / 365.0)::numeric
		END as age,
		expl_id::bigint,
		normalized_id::integer AS matcat_id,
		pnom::numeric,
		dnom::numeric,
		length::numeric,
		slope::numeric,
		elev_delta::numeric,
		(demand / length)::numeric AS udemand,
		(n_connec / length)::numeric AS uconnec,
		(press_max - press_min)::numeric AS press_range,
		press_mean::numeric,
		(press_mean / (pnom::numeric * 10.0))::numeric AS press_mean_pnom,
		(press_max / (pnom::numeric * 10.0))::numeric AS press_max_pnom,
		vel_min::numeric,
		vel_max::numeric,
		vel_mean::numeric,
		ndvi::numeric AS ndvi_mean,
		broken::boolean

	FROM
		(
		SELECT 
			*, 
			NULL::date as leak_date,
			FALSE as broken
		FROM ws.ai_inventory
		
		UNION ALL

		SELECT 
			a.*, 
			data as leak_date,
			TRUE as broken
		FROM 
			ws.ai_inventory as a
			JOIN 
			ws.ai_leak as b
			USING (arc_id)
		) t
		JOIN ws.ai_hydraulics USING (arc_id)
		JOIN ws.ai_ndvi USING (arc_id)
		JOIN ws.ai_cat_mat m ON (m.source_id = matcat_id)

	WHERE 
		pnom::numeric > 0
			
	
