# Fiscal Year

## Method 1

#### Backend
- Serialize and return `user.company.config_template` in login.
- If `user.company.config_template` does not start with np `np`, also serialize and serialize start and end date for fiscal year selected for the company.

#### Frontend
- Persist `user.company.config_template` returned during login in state.
- If `user.company.config_template` starts with np, use Nepali fiscal year, as is.
- Else, use serialized start and end dates for FY start and end month and day in calendar.

## Method 2

#### Data
- Use `np` as config_template for Nepali companies.
- Use `us` as config_template for US companies.

#### Backend
- Serialize and return `user.company.config_template` in login.

#### Frontend
- If `user.company.config_template` starts with np, use Nepali fiscal year in calendar, as is.
- If `user.company.config_template` starts with us, use Nepali fiscal year in calendar, as is.

