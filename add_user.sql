# for development use
# create user
CREATE USER 'lohnexport'@'%' IDENTIFIED BY 'xxx';
# grant privileges
GRANT SELECT on nextcloud.oc_users to 'lohnexport'@'%';

# for production use
# create user
CREATE USER 'lohnexport'@'localhost' IDENTIFIED BY 'xxx';
# grant privileges
GRANT SELECT on nextcloud.oc_users to 'lohnexport'@'localhost';