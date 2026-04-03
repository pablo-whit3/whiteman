CREATE OR REPLACE PROCEDURE insert_or_update(p_name TEXT, p_phone TEXT)
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO contacts(name, phone) VALUES(p_name, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE PROCEDURE insert_many(names TEXT[], phones TEXT[])
AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(names, 1) LOOP
        
        IF phones[i] ~ '^\+\d-\d{3}-\d{3}-\d{2}-\d{2}$' THEN
            INSERT INTO contacts(name, phone)
            VALUES(names[i], phones[i]);
        ELSE
            RAISE NOTICE 'Invalid phone for %: %', names[i], phones[i];
        END IF;

    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE delete_user(value TEXT)
AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = value OR phone = value;
END;
$$ LANGUAGE plpgsql;