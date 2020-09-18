-- RAW
DROP VIEW IF EXISTS ws.v_ai_leak_arc_raw CASCADE;
CREATE VIEW ws.v_ai_leak_arc_raw AS
    SELECT 
        arc_id,
        presszone_id,
        expl_id,
        age,
        matcat_id,
        length,
        pnom,
        dnom,
        slope,
        elev_delta,
        udemand,
        uconnec,
        press_range,
        press_mean,
        press_mean_pnom,
        press_max_pnom,
        vel_max,
        vel_mean,
        ndvi_mean,
        broken

    FROM 
        ws.v_ai_leak_arc_aux;


-- LEAK
DROP VIEW IF EXISTS ws.v_ai_leak_arc_leak CASCADE;

CREATE VIEW ws.v_ai_leak_arc_leak AS
    SELECT * FROM 
        ws.v_ai_leak_arc_raw

    WHERE
        broken = TRUE and
        pnom::numeric >= (SELECT value FROM ws.config_param_system WHERE parameter = 'treshold_arc_pnom_min')::numeric and
		length >= (SELECT value FROM ws.config_param_system WHERE parameter = 'treshold_arc_length_min')::numeric and
        length <= (SELECT value FROM ws.config_param_system WHERE parameter = 'treshold_arc_length_max')::numeric and
		slope <= (SELECT value FROM ws.config_param_system WHERE parameter = 'treshold_arc_slope_max')::numeric;

CREATE MATERIALIZED VIEW ws.v_ai_leak_arc_leak_train AS
SELECT * from ws.v_ai_leak_arc_leak WHERE random() < 0.8;

CREATE MATERIALIZED VIEW ws.v_ai_leak_arc_leak_valid AS
SELECT * FROM ws.v_ai_leak_arc_leak a WHERE NOT EXISTS (SELECT FROM ws.v_ai_leak_arc_leak_train WHERE a.arc_id = arc_id);


-- NO LEAK
DROP VIEW IF EXISTS ws.v_ai_leak_arc_noleak CASCADE;

CREATE VIEW ws.v_ai_leak_arc_noleak AS
    SELECT * FROM 
        ws.v_ai_leak_arc_raw

    WHERE
        broken = FALSE and
		pnom::numeric >= (SELECT value FROM ws.config_param_system WHERE parameter = 'treshold_arc_pnom_min')::numeric and
		length >= (SELECT value FROM ws.config_param_system WHERE parameter = 'treshold_arc_length_min')::numeric and
        length <= (SELECT value FROM ws.config_param_system WHERE parameter = 'treshold_arc_length_max')::numeric and
		slope <= (SELECT value FROM ws.config_param_system WHERE parameter = 'treshold_arc_slope_max')::numeric;

CREATE MATERIALIZED VIEW ws.v_ai_leak_arc_noleak_train AS
SELECT * from ws.v_ai_leak_arc_noleak WHERE random() < 0.8;

CREATE MATERIALIZED VIEW ws.v_ai_leak_arc_noleak_valid AS
SELECT * FROM ws.v_ai_leak_arc_noleak a WHERE NOT EXISTS (SELECT FROM ws.v_ai_leak_arc_noleak_train WHERE a.arc_id = arc_id);