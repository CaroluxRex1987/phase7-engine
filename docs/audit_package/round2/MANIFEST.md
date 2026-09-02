# Audit package manifest

- Built: 2026-09-02T08:10:22.361347+00:00
- Repository HEAD: `2f8b7ed100782c124d8244506ec9a4669e3f60aa`
- Round: round2
- Source files: 34
- Test files: 26

Every file's SHA-256 is listed below, computed from the exact bytes placed in
the bundle. If a file in the bundle does not hash to the value here, the
package was altered after it was built and you should say so in your report.

## Source

- `__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `live_trading.py` — 6053 bytes — `fdba9b6d7b3693b4e0453867b1412f264912b9ac846e1ac92db5d295eb24e19b`
- `main.py` — 3092 bytes — `6365fac5c98588a82bb66f2eea114741a0c55499cd2accef06ed914a61184df8`
- `core/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `core/config.py` — 4660 bytes — `d4526d2159e0255713b879c260393686b208ae991cd8b998e118a450331f6cf6`
- `core/decision_contract.py` — 14977 bytes — `cdc726e77762e9c5d3b2b9db7a9bd14a6c829baeaf82d13fa43cbdfbacf4a620`
- `core/decision_log.py` — 9377 bytes — `db52c55e8dfd65a949c6e14ad64e483a1bb246b10475d8a393da07ca74169788`
- `core/engine_core.py` — 54622 bytes — `0aecae170943346340d7528cb2a00458cd5caed03682281f8447bc33fbcb528d`
- `core/lineage.py` — 15772 bytes — `281c845a96019613fc4c51deda2ad8380729a2be860ecf25121af9e3f616637a`
- `core/panel_render.py` — 22278 bytes — `e8ae92cbb3c47329bfb980eedc8a107f0e6de5fda21bf9e5292e872315acd22b`
- `data/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `data/data_fetcher.py` — 13615 bytes — `525e5e660c2e89410fd557beae3ebc55ab9057301826a1683f37323b32833459`
- `data/validation.py` — 13423 bytes — `7026bbb32850ebab417896c4e75beb2760a9bca6f214904db445b743acf0c539`
- `indicators/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `indicators/indicators.py` — 37994 bytes — `6fa9da95dfe4e6fd14dea0d4bc46b87344fc55895fe4ebb82df17eacdd3c7cbf`
- `indicators/trend_health.py` — 21292 bytes — `8eff8f89581feca1cca8f608ad5e39c20358c19b1ae85a6beeaea786f7cba143`
- `indicators/volume_profile.py` — 10070 bytes — `710a449b2209136616f2ef4201fbcbb4e03a15f072bf77664a9e9e46db255e17`
- `models/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `models/bias_engine.py` — 19233 bytes — `ec7b23c4b5cf1d460c9cf3489062a40e8ee507234b43d0e23a903129feed7d03`
- `models/btc_context.py` — 3769 bytes — `5478304590310165064abc59dba86f2095ead6451e16fcd4c94d7a2ebaaf9c3c`
- `models/decision_model.py` — 34681 bytes — `05689d6ac24836850af1f5f66cd17dd368d5f64e3000892d438533b35d93dbfe`
- `models/entry_model.py` — 14422 bytes — `701cc129da3c241351fb3b8d6113e4274c07951265f8231f569d12f0771062d2`
- `models/exit_model.py` — 8335 bytes — `c7200291fa5e35290ba0d08821c64ab4e887b7cb0b26e1437866f7848f35a69d`
- `models/risk_model.py` — 14175 bytes — `d716e8450ee21790e9ada3c688e18ed8739c3075293b2ff91cc4a693e070cb55`
- `models/signal_router.py` — 22334 bytes — `fc204dbb086de3566c0648406ddcf72e3e1ffbc3786468d1601f4edda45dcf83`
- `structure/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `structure/structure.py` — 19965 bytes — `afa3c10ce4bb8ef8a7a038c5d030388af0db1f7e96e8731f5d425673774c4af2`
- `utils/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `utils/plotting.py` — 12097 bytes — `6c42b07a4bbc6d0e9c0b49de36a22812ec5d4f935eef57f5373f63b9252785bb`
- `pytest.ini` — 102 bytes — `c14b489a30afe60312242394d2e54d37d23e99ccef8d68f203807b76e325c758`
- `requirements.txt` — 613 bytes — `eda215b82092fd3e07191cd869bb90a8d7f4a37a67836bc9322906da96ee382d`
- `requirements-dev.txt` — 273 bytes — `0c67eda7468aa430882a1c656d55f83d074ae34919d2019b32bd2d59fb9edecc`
- `.gitattributes` — 415 bytes — `1292f94e64939668f892d09d37d2001b3116899b8c6fbc294942ea841a5f137f`
- `.gitignore` — 2094 bytes — `3bafa2d6db451e7a57521d5f887206390e86e3d12461bf92353c0ecb0de2da40`

## Tests

- `run_tests.py` — 6767 bytes — `fc4717aca0ccf0c69a0583a7a5fd515df8c5a5c8cde7695483060a49449136f2`
- `test_live.py` — 275 bytes — `31e48fb0ee08cd7e67ba7a09508d6a39ddf3d8f1729b55ee12c35c51e08af46e`
- `tests/conftest.py` — 2671 bytes — `35359c364954d9022c0bfe84110ba11782d4bd3e9f3da51dea6d8f7a204bb345`
- `tests/test_clean_checkout.py` — 3892 bytes — `52abff0851110cd3f84d3ecf600df07eaeccc811470ecf2cbcf22a185ffb5388`
- `tests/test_data_integrity.py` — 11857 bytes — `dfe5fb5d41ad0a4da5eeea81b21aeb9e4ced2d304c6bf167341e6f93c1b809fc`
- `tests/test_decision_bar_integrity.py` — 19738 bytes — `2f6191d0f4b84c6e212ac08d713b9ab1f4e2b19d819c28d2f846b490adf5f757`
- `tests/test_decision_contract.py` — 14051 bytes — `a568748a2b490ddf52c51b35e2066c9f697d994843e70a00c9fe33e96d7de186`
- `tests/test_degraded_state.py` — 23110 bytes — `2db11165ddcf73b380ff88505702a1bcac585f7c8f0568f19aeb6a3f651a50e2`
- `tests/test_direction_source.py` — 11620 bytes — `f8da77db213bd634c0ea821832160c6d3d5c615e40ad9ba697def487a4ae9f8c`
- `tests/test_execution_surface.py` — 7740 bytes — `cc15f8dfcd8af008a2b9f7f5c627aa750bc43dcca7260081cad02fdf75f5358b`
- `tests/test_exit_model_removal.py` — 9504 bytes — `5672ac971c95cf3d463c5494c914f3f3b80c09a60efd9cde8fbdebe957579cdc`
- `tests/test_explicit_configuration.py` — 15978 bytes — `2fa43b70b96ee02117465a684c1d54053f09f05108ad8eefd7d2ba944660823c`
- `tests/test_frame_ownership.py` — 13052 bytes — `1b84dd8418aac72ff9ec008d047b53e55795fec5e249a858537db65b86866000`
- `tests/test_golden_path.py` — 24763 bytes — `9fc7d0a1d2a333fd0e05d0cc289bd941bd1e27f20fc9cc34583d6ef81087dfc4`
- `tests/test_imports.py` — 12449 bytes — `e8f2948130e42bd0904c13125f4193f27b2412a66fb50656ced381f75214d752`
- `tests/test_lineage.py` — 30222 bytes — `85c01ba6b765044338a1a5f385e99333c04982b02e99b6f6ff75b58e61b6e2f0`
- `tests/test_no_circular_reasoning.py` — 15915 bytes — `53cc7bbffe137873d0d051b354477e3ba8d88f799af621cd7ef86d6e6eeb8ef7`
- `tests/test_no_dead_columns.py` — 6712 bytes — `c40abeb73a8b243ce95780984793ce7b0f81b8c66559bce20b3ac063b7657787`
- `tests/test_no_lookahead.py` — 16647 bytes — `e3fb368393e0f0e4894df5c02c1642c4ec32241a03fe3268bdaacbe12d9c3f1e`
- `tests/test_no_position_sizing.py` — 11736 bytes — `9288db678429928fd15dbcb92ad059ece9f89e329d8487a8a4d45593ae6de4c0`
- `tests/test_no_risk_free_conviction.py` — 10503 bytes — `7ea2a33652fbea61a1d6521c764fda9daa3cc76140defd35990bd24c2ea2570f`
- `tests/test_pinned_source.py` — 9927 bytes — `e4c7a5f76a3ccafacb1e0e257be3ccd66403a4e5b914263e042c83cd34c8b46f`
- `tests/test_smoke.py` — 6423 bytes — `142fabc300fa8cd73fb3670a64e48fad7ea5be2e1b26ee9765eb9474f8c2cdc4`
- `tests/test_timeframe_disagreement.py` — 14347 bytes — `2426e40afe99d66086913600200f83c7ac386346f67d7bd3bfd5143655316b5f`
- `tests/test_traceability.py` — 10342 bytes — `6dfbc3cb292e124152bc2aa95c5a9c3c2aa129b96e7fe2c860291172f29a0080`
- `tests/test_unwritable_log_dir.py` — 8470 bytes — `777b32973a8b30f0ffb8ead6a84eb270b8c88a8ed2ebec24e54244cc83d2c84e`
