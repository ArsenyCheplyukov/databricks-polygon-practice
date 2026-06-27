.PHONY: up down generate-data test test-l1 test-l2 test-l3 test-l4 test-l5 logs clean

up:
	docker compose up -d spark

up-lineage:
	docker compose --profile lineage up -d

up-unity:
	docker compose --profile unity up -d

down:
	docker compose --profile lineage --profile unity down

generate-data:
	docker compose exec -T spark python data/generate.py --scale small

test:
	docker compose exec -T spark pytest -q

test-l1:
	docker compose exec -T spark pytest -q layer1_delta_core/tests

test-l2:
	docker compose exec -T spark pytest -q layer2_delta_ops/tests

test-l3:
	docker compose exec -T spark pytest -q layer3_medallion/tests

test-l4:
	docker compose exec -T spark pytest -q layer4_lineage/tests

test-l5:
	docker compose exec -T spark pytest -q layer5_unity_catalog/tests

logs:
	docker compose logs -f spark

clean:
	docker compose --profile lineage --profile unity down -v
	rm -rf data/generated spark-warehouse metastore_db derby.log .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
