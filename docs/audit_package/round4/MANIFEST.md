# Audit package manifest

- Built: 2026-09-05T15:41:11.392932+00:00
- Repository HEAD: `417cadf7436f50802e148e02de05f95ab7af6597`
- Round: round4
- Source files: 34
- Test files: 37

Every file's SHA-256 is listed below, computed from the exact bytes placed in
the bundle. If a file in the bundle does not hash to the value here, the
package was altered after it was built and you should say so in your report.

## Source

- `__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `live_trading.py` — 8558 bytes — `f27b10897e99618a8068adbac6efe4e25b01703b35aaf17539aea9d7eb248e33`
- `main.py` — 3092 bytes — `6365fac5c98588a82bb66f2eea114741a0c55499cd2accef06ed914a61184df8`
- `core/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `core/config.py` — 5640 bytes — `379d996999fe5a74335af877717778d105ebca066b504c21b02d05a18aeea7b0`
- `core/decision_contract.py` — 15586 bytes — `e3c88cda35705ff031d326287810116d57743a56abf61d13fd3b32f6c93f1762`
- `core/decision_log.py` — 10871 bytes — `eeedf23c7454217422184079e84aabfdab78befe9478c60bd3583197f272b3a7`
- `core/engine_core.py` — 68886 bytes — `b5b565f3b654346981a479753e49b7827167f8e9b051215ebd7ba8f87c49ee65`
- `core/lineage.py` — 15772 bytes — `281c845a96019613fc4c51deda2ad8380729a2be860ecf25121af9e3f616637a`
- `core/panel_render.py` — 31128 bytes — `d2f97b03d2e5ee82d106b6a22f70691362a2b056e2f9dec15e7e515b3722a94c`
- `data/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `data/data_fetcher.py` — 15463 bytes — `8a9c7021773bd96008628442acfcf4951a493af47f7498d7e6637b85c8c3b256`
- `data/validation.py` — 13423 bytes — `7026bbb32850ebab417896c4e75beb2760a9bca6f214904db445b743acf0c539`
- `indicators/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `indicators/indicators.py` — 41655 bytes — `f8fb3e42174950c8d90f2729ecf3dfbe78323f264104e6f72c8d58ee01f2a7c0`
- `indicators/trend_health.py` — 22999 bytes — `f9086329d75cc3e58e0a2a7ad446e4665d57957b2c874a39ed0c6311235680fe`
- `indicators/volume_profile.py` — 10070 bytes — `710a449b2209136616f2ef4201fbcbb4e03a15f072bf77664a9e9e46db255e17`
- `models/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `models/bias_engine.py` — 20726 bytes — `7bff8b388fea461063930e92a1be221161dd20e882268d5d04ae7a6433b34e75`
- `models/btc_context.py` — 8027 bytes — `bc10093d956207e582ece3c40e99b5ee5aba3ef84dd9946f0bdca90060609cc0`
- `models/decision_model.py` — 39230 bytes — `76d4b8c5c911cd507b0332fa898a131510ed6970d448afcc26ed6ead16282b86`
- `models/entry_model.py` — 23680 bytes — `862c3a2e0275b210fe9913d9bcae04495367fb9520c80d09057e60e4cc304db8`
- `models/exit_model.py` — 8335 bytes — `c7200291fa5e35290ba0d08821c64ab4e887b7cb0b26e1437866f7848f35a69d`
- `models/risk_model.py` — 16688 bytes — `37e16ee69ff7c195d356f28825b5066a57e9983ceb0a5d71e863d09be55bf3b9`
- `models/signal_router.py` — 24966 bytes — `bb305512b068d2c5eacab8f7ff804099e0d3976f80eed90209a6ed09b689a7c6`
- `structure/__init__.py` — 0 bytes — `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `structure/structure.py` — 23311 bytes — `8e2f86c8b9746585260dcdbeaa44530c0d89b66b16fc30ae52ffea0f515eabec`
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
- `tests/test_btc_correlation_alignment.py` — 14854 bytes — `e9f797521ccddc63d63ebee8c1248eb2c63b6635a9e6104c89b813b02616b527`
- `tests/test_clean_checkout.py` — 3892 bytes — `52abff0851110cd3f84d3ecf600df07eaeccc811470ecf2cbcf22a185ffb5388`
- `tests/test_data_integrity.py` — 11857 bytes — `dfe5fb5d41ad0a4da5eeea81b21aeb9e4ced2d304c6bf167341e6f93c1b809fc`
- `tests/test_decision_bar_integrity.py` — 19738 bytes — `2f6191d0f4b84c6e212ac08d713b9ab1f4e2b19d819c28d2f846b490adf5f757`
- `tests/test_decision_contract.py` — 14051 bytes — `a568748a2b490ddf52c51b35e2066c9f697d994843e70a00c9fe33e96d7de186`
- `tests/test_degraded_state.py` — 23110 bytes — `2db11165ddcf73b380ff88505702a1bcac585f7c8f0568f19aeb6a3f651a50e2`
- `tests/test_direction_source.py` — 11620 bytes — `f8da77db213bd634c0ea821832160c6d3d5c615e40ad9ba697def487a4ae9f8c`
- `tests/test_entry_score_reconciles.py` — 15006 bytes — `90aeae3db22f13b2c7fc1d1288b6f0ad9c3dc7bae75b95ade3ef692012a24421`
- `tests/test_entry_zone_is_measured.py` — 15247 bytes — `4935575ec4868739255fe1dade0304a7ec7f5cc47acf5ad3c668710943a5cef4`
- `tests/test_execution_surface.py` — 7740 bytes — `cc15f8dfcd8af008a2b9f7f5c627aa750bc43dcca7260081cad02fdf75f5358b`
- `tests/test_exit_model_removal.py` — 9504 bytes — `5672ac971c95cf3d463c5494c914f3f3b80c09a60efd9cde8fbdebe957579cdc`
- `tests/test_explicit_configuration.py` — 15978 bytes — `2fa43b70b96ee02117465a684c1d54053f09f05108ad8eefd7d2ba944660823c`
- `tests/test_fetch_and_import_hygiene.py` — 10934 bytes — `52168a09482de293e3d76552f7bead68019d3902dd2f42291b8cd58ba09beb5a`
- `tests/test_frame_ownership.py` — 13052 bytes — `1b84dd8418aac72ff9ec008d047b53e55795fec5e249a858537db65b86866000`
- `tests/test_golden_path.py` — 24763 bytes — `9fc7d0a1d2a333fd0e05d0cc289bd941bd1e27f20fc9cc34583d6ef81087dfc4`
- `tests/test_imports.py` — 12449 bytes — `e8f2948130e42bd0904c13125f4193f27b2412a66fb50656ced381f75214d752`
- `tests/test_lineage.py` — 30222 bytes — `85c01ba6b765044338a1a5f385e99333c04982b02e99b6f6ff75b58e61b6e2f0`
- `tests/test_macro_agreement.py` — 5451 bytes — `baaa833bd79230ec9a8811db78fed69b31a0b6a368e5cd7552350a7e5c06cbd3`
- `tests/test_minimum_bias_strength.py` — 7158 bytes — `e312ef5020ff20dbb5dd395e6f53c4577b489a44455c5a6f3cad8bd24963c271`
- `tests/test_no_circular_reasoning.py` — 15915 bytes — `53cc7bbffe137873d0d051b354477e3ba8d88f799af621cd7ef86d6e6eeb8ef7`
- `tests/test_no_dead_columns.py` — 6712 bytes — `c40abeb73a8b243ce95780984793ce7b0f81b8c66559bce20b3ac063b7657787`
- `tests/test_no_fabricated_fallbacks.py` — 11826 bytes — `bd3a7960512e7f3c662e74820a06107294efcfe2e905db375b77ab462f1ffef8`
- `tests/test_no_lookahead.py` — 16647 bytes — `e3fb368393e0f0e4894df5c02c1642c4ec32241a03fe3268bdaacbe12d9c3f1e`
- `tests/test_no_position_sizing.py` — 11736 bytes — `9288db678429928fd15dbcb92ad059ece9f89e329d8487a8a4d45593ae6de4c0`
- `tests/test_no_risk_free_conviction.py` — 11215 bytes — `c648f076c1e2afaccd401da66226f36bbdb5139ed37f55fd9621f017c5d9295c`
- `tests/test_pinned_source.py` — 9927 bytes — `e4c7a5f76a3ccafacb1e0e257be3ccd66403a4e5b914263e042c83cd34c8b46f`
- `tests/test_risk_fingerprint.py` — 10800 bytes — `b6fafa8e70bd5434858d0016aa4f7ab7891c3c2cc5d7665a612577a39f608255`
- `tests/test_smoke.py` — 6423 bytes — `142fabc300fa8cd73fb3670a64e48fad7ea5be2e1b26ee9765eb9474f8c2cdc4`
- `tests/test_structure_fallbacks.py` — 10158 bytes — `5e2fa359d22cd3c85b32647db2e016fc22bc597e8b304c511487c02bcc10fde1`
- `tests/test_timeframe_disagreement.py` — 14347 bytes — `2426e40afe99d66086913600200f83c7ac386346f67d7bd3bfd5143655316b5f`
- `tests/test_traceability.py` — 12037 bytes — `b9401b553863f4a2894c21368bda1df42c021807fba0ef7c76484299033bccec`
- `tests/test_trend_direction_source.py` — 6462 bytes — `ef5bd5503b30340a2c8366547a8ba4daff28f22d0d7fd456d070ddc3a8207678`
- `tests/test_unwritable_log_dir.py` — 10351 bytes — `8b81e5b2a22c925c96f62b3e46f997519ee6394006aa5af27162c275e1a4a233`
- `tests/test_volume_agreement.py` — 7830 bytes — `09ba698fa45c53d259e9bb691cfbfef85c699efa0b741b43c00424c5148a8ba0`
