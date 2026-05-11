CREATE OR REPLACE FUNCTION search_pattern(pattern TEXT)
RETURNS TABLE(id INT, name VARCHAR, email VARCHAR, birthday DATE, group_name VARCHAR, phone VARCHAR, type VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT c.id, c.name, c.email, c.birthday, g.name, p.phone, p.type FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    LEFT JOIN phones p ON c.id = p.contact_id
    WHERE c.name ILIKE '%' || pattern || '%'
        OR c.email ILIKE '%' || pattern || '%'
        OR p.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paginated(limit_val INT, offset_val INT)
RETURNS TABLE(
    id INT,
    name VARCHAR,
    email VARCHAR,
    phone VARCHAR,
    type VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.email, p.phone, p.type
    FROM contacts c
    LEFT JOIN phones p ON c.id = p.contact_id
    ORDER BY c.id
    LIMIT limit_val OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;