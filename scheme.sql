CREATE TABLE "request" (
  "id" SERIAL NOT NULL PRIMARY KEY,
  "date" TIMESTAMP,
--  "coordinate" TEXT,
  "telegraph" TEXT,
  "area_id" INTEGER
);

SELECT AddGeometryColumn ('public', 'request', 'coordinate', 4326, 'POINT', 2);


CREATE TABLE "area" (
  "id" SERIAL NOT NULL,
  "area_name" TEXT
--  "coordinates" TEXT
);

SELECT AddGeometryColumn ('public', 'area', 'coordinate', 4326, 'MULTIPOLYGON', 2);


ALTER TABLE "area" ADD CONSTRAINT "fk_area__id" FOREIGN KEY ("id") REFERENCES "request" ("id");

CREATE TABLE "area_type_directory" (
  "id" SERIAL NOT NULL,
  "name" TEXT,
  "hierarchy" INTEGER
);

ALTER TABLE "area_type_directory" ADD CONSTRAINT "fk_area_type_directory__id" FOREIGN KEY ("id") REFERENCES "area" ("id");

CREATE TABLE "category" (
  "id" SERIAL NOT NULL,
  "text" TEXT
);

ALTER TABLE "category" ADD CONSTRAINT "fk_category__id" FOREIGN KEY ("id") REFERENCES "request" ("id");

CREATE TABLE "organisation" (
  "id" SERIAL NOT NULL,
  "name" TEXT,
  "url" TEXT,
  "email" TEXT
);

ALTER TABLE "organisation" ADD CONSTRAINT "fk_organisation__id" FOREIGN KEY ("id") REFERENCES "area" ("id");

CREATE TABLE "status" (
  "id" SERIAL NOT NULL,
  "typename" TEXT,
  "hierarchy" INTEGER
);

ALTER TABLE "status" ADD CONSTRAINT "fk_status__id" FOREIGN KEY ("id") REFERENCES "request" ("id");

CREATE TABLE "template" (
  "id" SERIAL NOT NULL PRIMARY KEY,
  "text" TEXT
);

CREATE TABLE "area_template" (
  "area" INTEGER,
  "template" INTEGER,
  PRIMARY KEY ("area", "template")
);

CREATE INDEX "idx_area_template" ON "area_template" ("template");

ALTER TABLE "area_template" ADD CONSTRAINT "fk_area_template__area" FOREIGN KEY ("area") REFERENCES "area" ("id");

ALTER TABLE "area_template" ADD CONSTRAINT "fk_area_template__template" FOREIGN KEY ("template") REFERENCES "template" ("id");

CREATE TABLE "category_template" (
  "id" SERIAL NOT NULL,
  "category" INTEGER,
  "template" INTEGER,
  PRIMARY KEY ("category", "template")
);

CREATE INDEX "idx_category_template" ON "category_template" ("template");

ALTER TABLE "category_template" ADD CONSTRAINT "fk_category_template__category" FOREIGN KEY ("category") REFERENCES "category" ("id");

ALTER TABLE "category_template" ADD CONSTRAINT "fk_category_template__template" FOREIGN KEY ("template") REFERENCES "template" ("id");

CREATE TABLE "user" (
  "id" SERIAL NOT NULL,
  "name" TEXT,
  "surname" TEXT,
  "patronymic" TEXT,
  "email" TEXT,
  "password" TEXT
);

--ALTER TABLE "user" ADD CONSTRAINT "fk_user__id" FOREIGN KEY ("id") REFERENCES "request" ("id")