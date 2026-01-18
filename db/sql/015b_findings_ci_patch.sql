-- V20 CI columns patch (safe if columns already exist)
ALTER TABLE findings ADD COLUMN effect_size_type TEXT;
ALTER TABLE findings ADD COLUMN ci_lower REAL;
ALTER TABLE findings ADD COLUMN ci_upper REAL;