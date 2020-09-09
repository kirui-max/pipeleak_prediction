DROP VIEW IF EXISTS ws.v_ai_leak_minsector CASCADE;

CREATE VIEW ws.v_ai_leak_minsector AS
    SELECT 
        minsector_id,
        expl_id,
        total_length,
        leaks,
        age,
        CASE 
            WHEN mat_asb is NULL THEN 0
            ELSE mat_asb
        END as mat_asb,
        CASE 
            WHEN mat_tir is NULL THEN 0
            ELSE mat_tir
        END as mat_tir,
        CASE 
            WHEN mat_iro is NULL THEN 0
            ELSE mat_iro
        END as mat_iro,
        CASE 
            WHEN mat_pex is NULL THEN 0
            ELSE mat_pex
        END as mat_pex,
        CASE 
            WHEN mat_pvc is NULL THEN 0
            ELSE mat_pvc
        END as mat_pvc,
        CASE 
            WHEN mat_oth is NULL THEN 0
            ELSE mat_oth
        END as mat_oth,
        pnom,
        dnom,
        uconnec,
        slope,
        elev_delta,
        press_range,
        press_mean,
        press_mean_pnom,
        press_max_pnom,
        vel_min,
        vel_max,
        vel_mean,
        ndvi_mean,
        frequency

    FROM
        (SELECT
            minsector_id,
            expl_id,
            sum(length) as total_length,
            count(*) as leaks,
            sum(length * age) / sum(length) as age,
            sum(length * pnom) / sum(length) as pnom,
            sum(length * dnom) / sum(length) as dnom,
            sum(length * uconnec) / sum(length) as uconnec,
            sum(length * udemand) / sum(length) as udemand,
            sum(length * slope) / sum(length) as slope,
            sum(length * elev_delta) / sum(length) as elev_delta,
            sum(length * press_range) / sum(length) as press_range,
            sum(length * press_mean) / sum(length) as press_mean,
            sum(length * press_mean_pnom) / sum(length) as press_mean_pnom,
            sum(length * press_max_pnom) / sum(length) as press_max_pnom,
            min(vel_min) as vel_min,
            max(vel_max) as vel_max,
            sum(length * vel_mean) / sum(length) as vel_mean,
            sum(length * ndvi_mean) / sum(length) as ndvi_mean,
            (1000 * count(*)) / (((SELECT value FROM ws.config_param_system WHERE parameter = 'dataset_leak_interval')::numeric) * sum(length)) as frequency

        FROM ws.v_ai_leak_arc_aux

        GROUP BY minsector_id, expl_id, presszone_id) a

        JOIN 

        (SELECT ct.* FROM 
            crosstab('
            SELECT 
                minsector_id,
                matcat_id,
                length / total_length as weigth

            FROM 
                
                (SELECT
                    minsector_id::integer,
                    sum(length)::numeric as total_length

                FROM ws.v_ai_leak_arc_aux

                WHERE broken = TRUE

                GROUP BY minsector_id) a

            JOIN

                (SELECT

                    minsector_id,
                    matcat_id,
                    sum(length) as length

                FROM ws.v_ai_leak_arc_aux

                WHERE broken = TRUE

                GROUP BY minsector_id, matcat_id) b

            USING (minsector_id)'::text, 'VALUES (''1''),(''2''),(''3''),(''4''),(''5''),(''0'')'::text) 

            ct(
                minsector_id integer, 
                mat_asb numeric, 
                mat_tir numeric, 
                mat_iro numeric, 
                mat_pex numeric, 
                mat_pvc numeric, 
                mat_oth numeric
            )) b
        
        USING (minsector_id)

    WHERE 
        frequency > 0 and
        frequency < (SELECT value FROM ws.config_param_system WHERE parameter = 'treshold_minsector_frequency_max')::numeric;


create materialized view ws.v_ai_leak_minsector_train as
select * from ws.v_ai_leak_minsector where random() < 0.8;

create materialized view ws.v_ai_leak_minsector_valid as
select * from ws.v_ai_leak_minsector a where not exists (select from ws.v_ai_leak_minsector_train where a.minsector_id = minsector_id);
