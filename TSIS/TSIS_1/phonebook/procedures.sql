CREATE OR REPLACE PROCEDURE delete_user(value TEXT)
AS $$
BEGIN
    DELETE FROM contacts
    WHERE name = value 
        OR id IN (
            SELECT contact_id FROM phones WHERE phone = value
        );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
AS $$
DECLARE
    cid INT;
BEGIN
    SELECT id INTO cid FROM contacts WHERE name = p_contact_name;

        INSERT INTO phones(contact_id, phone, type)
        VALUES(cid, p_phone, p_type);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
AS $$
DECLARE
    gid INT;
BEGIN
    INSERT INTO groups(name)
    VALUES(p_group_name)
    ON CONFLICT(name) DO NOTHING;

    SELECT id INTO gid FROM groups WHERE name = p_group_name;
    UPDATE contacts 
    SET group_id = gid WHERE name = p_contact_name;
END;
$$ LANGUAGE plpgsql;