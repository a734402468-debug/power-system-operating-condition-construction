# N-T2: linked expression input

Extract from the recorded input. Record-identification fields are omitted and JSON is indented for readability; electrical requirements, supplied numerical values, instructions, and syntax examples are retained. The two forms use different instructions and examples, as described in the [paired comparison](../results/README.md#requirement-checks).

## System message

```text
Return one compact JSON object using the supplied method contract and independent fictional syntax example. Translate the unchanged complete Chinese requirements, selecting exact public object/set/reference/policy IDs, interval directions and explicit stages. No full PF paths, executable code, long quotations, precise alpha, reference solution, invented equipment or relaxed requirements. Continuous amplitude is solved jointly by the common tool. Only a public contract or execution error permits one correction; no hidden semantic answer will be supplied. Reasoning is not executable; put the final specification in message.content within 4096 answer tokens.
```

## User message

```json
{
  "original_requirements": "用途：构造相反集合方向的负荷重分配测试状态，比较相同输入总量下的位置效应。固定转出统计成员L3，其余设备自由协调；不称线路潮流反转。\n研究者定义的集合负荷转移需求 N-T2。\nC1：最终从{L2=lod_101_1,L3=lod_102_1,L5=lod_104_1}向{L1=lod_100_1,L4=lod_103_1,L6=lod_105_1}转移0.2 MW有功输入：转出集合plini输入和相对base_v1减少该量，转入集合增加该量。仅最终要求转移完成。\nC2：集合内部自由协调分配，不要求比例或相同倍率、等量变化；固定成员仍参与集合总量统计但其变化必须为零。\nC3：六负荷{L1=lod_100_1,L2=lod_101_1,L3=lod_102_1,L4=lod_103_1,L5=lod_104_1,L6=lod_105_1}的plini输入和在基准及每个接受状态（含最终）保持base_v1的输入和，不将其称为实际系统总负荷或发电保持。\nC4：六负荷各自保持自身基准Q/P，P=P0×alpha、Q=Q0×alpha，从base_v1计算、禁止累乘；在基准及每个接受状态（含最终）生效。\nC5：六负荷绝对倍率均在[0.99,1.02]内；{L3=lod_102_1}的P/Q保持基准，其余五个负荷允许调整。边界和固定项在基准及每个接受状态（含最终）生效。\nC6：{V1=100 Glen Lyn,V2=101 Wythe,V3=102 Smythe,V4=103 Claytor,V5=104 Hancock,V6=105 Roanoke}的电压在基准及每个接受状态（含最终）分别保持自身基准电压±0.005 pu，不是六母线共享同一绝对区间。\nC7：其他负荷输入、拓扑、共享设备类型、控制及潮流配置保持不变；沿用登记的有限参考机组边界检查，不附加全网健康要求。基准不必满足仅最终目标；不合格试算不是接受状态，不要求虚构连续路径。\n精度采用precision-policy-v1：有功转移/输入和误差≤1.3636184692382813e-05 MW；各自Q/P残差≤3.3364502601314728e-06 Mvar；倍率读回误差≤1e-07；组内同倍率读回误差≤2e-07；固定P/Q精确恢复，误差0；电压以所列端点验收，附加放宽量0 pu。存储预算已包含在上述精度中，不再叠加。",
  "device_directory": {
    "L1": {
      "kind": "load",
      "name": "lod_100_1",
      "baseline": {
        "qlini": 18.0,
        "plini": 160.0
      },
      "units": {
        "plini": "MW",
        "qlini": "Mvar"
      },
      "connected_voltage_id": "V1",
      "input_mode": "verified fixed balanced static PQ; unit scale"
    },
    "L2": {
      "kind": "load",
      "name": "lod_101_1",
      "baseline": {
        "qlini": 15.0,
        "plini": 20.676830291748047
      },
      "units": {
        "plini": "MW",
        "qlini": "Mvar"
      },
      "connected_voltage_id": "V2",
      "input_mode": "verified fixed balanced static PQ; unit scale"
    },
    "L3": {
      "kind": "load",
      "name": "lod_102_1",
      "baseline": {
        "qlini": 3.0,
        "plini": 5.0129499435424805
      },
      "units": {
        "plini": "MW",
        "qlini": "Mvar"
      },
      "connected_voltage_id": "V3",
      "input_mode": "verified fixed balanced static PQ; unit scale"
    },
    "L4": {
      "kind": "load",
      "name": "lod_103_1",
      "baseline": {
        "qlini": 16.0,
        "plini": 21.871719360351562
      },
      "units": {
        "plini": "MW",
        "qlini": "Mvar"
      },
      "connected_voltage_id": "V4",
      "input_mode": "verified fixed balanced static PQ; unit scale"
    },
    "L5": {
      "kind": "load",
      "name": "lod_104_1",
      "baseline": {
        "qlini": 25.0,
        "plini": 34.48405075073242
      },
      "units": {
        "plini": "MW",
        "qlini": "Mvar"
      },
      "connected_voltage_id": "V5",
      "input_mode": "verified fixed balanced static PQ; unit scale"
    },
    "L6": {
      "kind": "load",
      "name": "lod_105_1",
      "baseline": {
        "qlini": 26.0,
        "plini": 28.4083309173584
      },
      "units": {
        "plini": "MW",
        "qlini": "Mvar"
      },
      "connected_voltage_id": "V6",
      "input_mode": "verified fixed balanced static PQ; unit scale"
    },
    "V1": {
      "kind": "voltage",
      "name": "100 Glen Lyn",
      "baseline_voltage_pu": 1.0169999877014881
    },
    "V2": {
      "kind": "voltage",
      "name": "101 Wythe",
      "baseline_voltage_pu": 0.986385013072658
    },
    "V3": {
      "kind": "voltage",
      "name": "102 Smythe",
      "baseline_voltage_pu": 0.9812397545453265
    },
    "V4": {
      "kind": "voltage",
      "name": "103 Claytor",
      "baseline_voltage_pu": 1.0100000181018234
    },
    "V5": {
      "kind": "voltage",
      "name": "104 Hancock",
      "baseline_voltage_pu": 0.9710000425318596
    },
    "V6": {
      "kind": "voltage",
      "name": "105 Roanoke",
      "baseline_voltage_pu": 0.9650000003123973
    }
  },
  "baseline_snapshot": {
    "state_id": "base_v1",
    "kind": "archived_original_baseline",
    "version": 1,
    "project_path": "\\MSI.IntUser\\PCL_Redistrib_261011_105851.IntPrj",
    "study_case_path": "\\MSI.IntUser\\PCL_Redistrib_261011_105851.IntPrj\\研究案例.IntPrjfolder\\研究案例.IntCase",
    "quantities": {
      "L1": {
        "qlini": 18.0,
        "plini": 160.0
      },
      "L2": {
        "qlini": 15.0,
        "plini": 20.676830291748047
      },
      "L3": {
        "qlini": 3.0,
        "plini": 5.0129499435424805
      },
      "L4": {
        "qlini": 16.0,
        "plini": 21.871719360351562
      },
      "L5": {
        "qlini": 25.0,
        "plini": 34.48405075073242
      },
      "L6": {
        "qlini": 26.0,
        "plini": 28.4083309173584
      },
      "V1": {
        "voltage_pu": 1.0169999877014881
      },
      "V2": {
        "voltage_pu": 0.986385013072658
      },
      "V3": {
        "voltage_pu": 0.9812397545453265
      },
      "V4": {
        "voltage_pu": 1.0100000181018234
      },
      "V5": {
        "voltage_pu": 0.9710000425318596
      },
      "V6": {
        "voltage_pu": 0.9650000003123973
      }
    }
  },
  "precision_policies": {
    "version": "precision-policy-v1",
    "policies": {
      "P_SUM_V1": {
        "unit": "MW",
        "user_allowed_error": 1.3636184692382813e-05,
        "effective_evaluation_tolerance": 1.3636184692382813e-05,
        "storage_policy": "existing preregistered float32 budget",
        "extra_storage_error_added": 0.0,
        "solver_policy": "retained-active-face-v1.1",
        "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
      },
      "QP_RESIDUAL_V1": {
        "unit": "Mvar",
        "user_allowed_error": 3.3364502601314728e-06,
        "effective_evaluation_tolerance": 3.3364502601314728e-06,
        "storage_policy": "existing preregistered float32 budget",
        "extra_storage_error_added": 0.0,
        "solver_policy": "retained-active-face-v1.1",
        "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
      },
      "ALPHA_READ_V1": {
        "unit": "dimensionless",
        "user_allowed_error": 1e-07,
        "effective_evaluation_tolerance": 1e-07,
        "storage_policy": "existing readback/exact-bound policy",
        "extra_storage_error_added": 0.0,
        "solver_policy": "retained-active-face-v1.1",
        "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
      },
      "FIXED_EXACT_V1": {
        "unit": "per_field",
        "user_allowed_error": 0.0,
        "effective_evaluation_tolerance": 0.0,
        "storage_policy": "existing readback/exact-bound policy",
        "extra_storage_error_added": 0.0,
        "solver_policy": "retained-active-face-v1.1",
        "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
      },
      "VOLTAGE_EDGE_ZERO_V1": {
        "unit": "pu",
        "user_allowed_error": 0.0,
        "effective_evaluation_tolerance": 0.0,
        "storage_policy": "existing readback/exact-bound policy",
        "extra_storage_error_added": 0.0,
        "solver_policy": "retained-active-face-v1.1",
        "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
      },
      "PROP_ALPHA_V1": {
        "unit": "dimensionless",
        "user_allowed_error": 2e-07,
        "effective_evaluation_tolerance": 2e-07,
        "storage_policy": "existing readback/exact-bound policy",
        "extra_storage_error_added": 0.0,
        "solver_policy": "retained-active-face-v1.1",
        "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
      }
    },
    "rule": "User allowed deviation, storage uncertainty and numerical residual checks are distinct. Existing user budget already includes its preregistered storage allowance; never add it twice."
  },
  "authorized_load_ids": [
    "L1",
    "L2",
    "L4",
    "L5",
    "L6"
  ],
  "output_contract": {
    "protocol": "shared-stage-set-v1.1/F/optional-provenance-v1",
    "root": {
      "OBJECT_REQUIRED_ONLY": {
        "specification": {
          "OBJECT_REQUIRED_ONLY": {
            "baseline_state": "ONE state ID string from supplied directory/state",
            "variables": {
              "OBJECT_REQUIRED_ONLY": {
                "objects": {
                  "ARRAY": "ONE load ID string from supplied directory/state",
                  "min_items": 1,
                  "max_items": "none",
                  "unique": true
                },
                "mapping": "ONE string: baseline_PQ_times_absolute_alpha"
              }
            },
            "constraints": {
              "ARRAY": "@constraint",
              "min_items": 1,
              "max_items": "none",
              "unique": false
            },
            "preserve": {
              "OBJECT_REQUIRED_ONLY": {
                "other_load_inputs": "boolean",
                "topology": "boolean",
                "control_settings": "boolean",
                "flow_settings": "boolean"
              }
            },
            "OPTIONAL_FIELDS": {
              "schema_version": "ONE string: state-reference-output-v2"
            }
          }
        },
        "plan": {
          "OBJECT_REQUIRED_ONLY": {
            "operation": "ONE string: solve | stop",
            "selected": {
              "ARRAY": "ONE load ID string from supplied directory/state",
              "min_items": 0,
              "max_items": "none",
              "unique": true
            },
            "reason": "string"
          }
        }
      }
    },
    "root_instruction": "The output itself has exactly specification and plan at its root. Do not wrap it in decision. Examples show the actual output root.",
    "cross_field_rules": {
      "revision": "steady-state-interface-v1",
      "constraint_objects": "Any role-compatible ID in device_directory may be referenced, including fixed loads. References do not grant write permission.",
      "authorized_load_ids": "Caller-supplied maximum set allowed to receive P/Q writes; separate from the full device directory.",
      "variables.objects": "Nonempty unique adjustable load IDs, a subset of authorized_load_ids. Do NOT list fixed or merely referenced objects here.",
      "plan.selected": "The subset of variables.objects chosen for this solve; unselected loads enter the numerical problem at their baseline inputs.",
      "solve": "operation=solve requires nonempty selected, contained in variables.objects and authorized_load_ids.",
      "stop": "operation=stop requires selected=[]. No numerical solve or PF action is requested.",
      "execution_mode": "compile_only/execute is a caller setting, not an electrical requirement or plan operation. compile_only does not imply stop.",
      "no_semantic_completion": "No automatic baseline, object selection, interval alteration, or omitted-condition repair. Source citations record provenance only."
    },
    "constraint_common": {
      "id": "string nonempty",
      "type": "ONE string: alpha_bounds | distribution | fixed_inputs | input_sum | proportional_distribution | qp_policy | transfer | voltage_bounds",
      "unit": "string",
      "clause": "ONE string: C1 | C2 | C3 | C4 | C5 | C6 | C7",
      "stages": {
        "type": "array",
        "items": "ONE string: baseline | every_accepted_state | final",
        "min_items": 1,
        "unique": true
      }
    },
    "constraint_specific_required": {
      "transfer": {
        "source": {
          "ARRAY": "ONE load ID string from supplied directory/state",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "destination": {
          "ARRAY": "ONE load ID string from supplied directory/state",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "amount": "@expression",
        "accuracy": "ONE string: P_SUM_V1"
      },
      "input_sum": {
        "objects": {
          "ARRAY": "ONE load ID string from supplied directory/state",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "target": "@expression",
        "accuracy": "ONE string: P_SUM_V1"
      },
      "qp_policy": {
        "objects": {
          "ARRAY": "ONE load ID string from supplied directory/state",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "state": "ONE state ID string from supplied directory/state",
        "policy": "ONE string: each_baseline_ratio",
        "accuracy": "ONE string: QP_RESIDUAL_V1"
      },
      "fixed_inputs": {
        "objects": {
          "ARRAY": "ONE load ID string from supplied directory/state",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "state": "ONE state ID string from supplied directory/state",
        "fields": {
          "ARRAY": "ONE string: plini | qlini",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "accuracy": "ONE string: FIXED_EXACT_V1"
      },
      "alpha_bounds": {
        "objects": {
          "ARRAY": "ONE load ID string from supplied directory/state",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "lower": "finite JSON number, not boolean/null",
        "upper": "finite JSON number, not boolean/null",
        "precision": "ONE string: ALPHA_READ_V1"
      },
      "voltage_bounds": {
        "objects": {
          "ARRAY": "ONE voltage ID string from supplied directory/state",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "bounds": "@bounds",
        "precision": "ONE string: VOLTAGE_EDGE_ZERO_V1"
      },
      "distribution": {
        "objects": {
          "ARRAY": "ONE load ID string from supplied directory/state",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "mode": "ONE string: free"
      },
      "proportional_distribution": {
        "objects": {
          "ARRAY": "ONE load ID string from supplied directory/state",
          "min_items": 1,
          "max_items": "none",
          "unique": true
        },
        "precision": "ONE string: PROP_ALPHA_V1"
      }
    },
    "constraint_units": {
      "transfer": "MW",
      "input_sum": "MW",
      "qp_policy": "Mvar",
      "alpha_bounds": "dimensionless",
      "voltage_bounds": "pu",
      "distribution": "dimensionless",
      "proportional_distribution": "dimensionless",
      "fixed_inputs": "per_field"
    },
    "expression_forms": {
      "dispatch_by": "op",
      "forms": {
        "literal": {
          "OBJECT_REQUIRED_ONLY": {
            "op": "ONE string: literal",
            "value": "finite JSON number, not boolean/null",
            "unit": "ONE string: MW | Mvar | pu | dimensionless"
          }
        },
        "baseline_sum": {
          "OBJECT_REQUIRED_ONLY": {
            "op": "ONE string: baseline_sum",
            "state": "ONE state ID string from supplied directory/state",
            "quantity": "ONE string: plini | qlini",
            "objects": {
              "ARRAY": "ONE load ID string from supplied directory/state",
              "min_items": 1,
              "max_items": "none",
              "unique": true
            }
          }
        },
        "baseline_value": {
          "OBJECT_REQUIRED_ONLY": {
            "op": "ONE string: baseline_value",
            "state": "ONE state ID string from supplied directory/state",
            "quantity": "ONE string: plini | qlini | voltage_pu",
            "object": "ONE registered ID string from supplied directory/state"
          }
        },
        "scale": {
          "OBJECT_REQUIRED_ONLY": {
            "op": "ONE string: scale",
            "factor": "finite JSON number, not boolean/null",
            "base": "@expression"
          }
        },
        "minimum": {
          "OBJECT_REQUIRED_ONLY": {
            "op": "ONE string: minimum",
            "items": {
              "ARRAY": "@expression",
              "min_items": 2,
              "max_items": 4,
              "unique": false
            }
          }
        }
      }
    },
    "interval_forms": {
      "dispatch_by": "kind",
      "forms": {
        "baseline_band": {
          "OBJECT_REQUIRED_ONLY": {
            "kind": "ONE string: baseline_band",
            "state": "ONE state ID string from supplied directory/state",
            "lower_offset": "finite JSON number, not boolean/null",
            "upper_offset": "finite JSON number, not boolean/null"
          }
        },
        "absolute": {
          "OBJECT_REQUIRED_ONLY": {
            "kind": "ONE string: absolute",
            "lower": "finite JSON number, not boolean/null",
            "upper": "finite JSON number, not boolean/null"
          }
        }
      }
    },
    "metadata_policy": {
      "specification.schema_version": "optional; if present must equal state-reference-output-v2",
      "program_envelope_state_reference_version": "state-reference-constraints-v1",
      "expanded_executable_version": "redistribution-constraints-v1",
      "physical_fields_added_or_corrected": false
    },
    "expression_depth_limit": 4,
    "rules": [
      "Each constraint combines ALL common and type-specific fields; no null, option arrays or extra fields.",
      "A raw number is NOT an expression. Wrap numbers as {\"op\":\"literal\",\"value\":NUMBER,\"unit\":\"MW\"}.",
      "Baseline references must name the chosen state/quantity/object set; binder does arithmetic only.",
      "All constraints are read literally; stage, direction, preservation and allocation are not supplied by the program."
    ],
    "shared_stage_semantics": {
      "baseline": [
        "baseline"
      ],
      "final": [
        "final"
      ],
      "every_accepted_state": [
        "baseline",
        "accepted",
        "final"
      ],
      "expansion": "Each constraint/call is copied ONLY for stages explicitly supplied; all physical fields are unchanged. No automatic baseline for final.",
      "same_condition_multiple_stages": "Use one row with a stages array when objects, bounds and all other conditions are identical.",
      "different_conditions": "Use separate rows for different objects/bounds/conditions. Never merge their requirements into one range.",
      "source_does_not_prove_semantics": true,
      "old_timing_field": "Use the stages array, not timing. stage_source is optional provenance."
    },
    "optional_stage_source": "Optional provenance string; exact quotations are not required and do not certify semantics."
  },
  "legal_output_example": {
    "specification": {
      "baseline_state": "fictional_base",
      "variables": {
        "objects": [
          "FA",
          "FB",
          "FC"
        ],
        "mapping": "baseline_PQ_times_absolute_alpha"
      },
      "constraints": [
        {
          "id": "move",
          "type": "transfer",
          "unit": "MW",
          "clause": "C1",
          "source": [
            "FA",
            "FB"
          ],
          "destination": [
            "FC"
          ],
          "amount": {
            "op": "scale",
            "factor": 0.005,
            "base": {
              "op": "baseline_sum",
              "state": "fictional_base",
              "quantity": "plini",
              "objects": [
                "FA",
                "FB"
              ]
            }
          },
          "accuracy": "P_SUM_V1",
          "stages": [
            "final"
          ]
        },
        {
          "id": "equal_source",
          "type": "proportional_distribution",
          "unit": "dimensionless",
          "clause": "C2",
          "objects": [
            "FA",
            "FB"
          ],
          "precision": "PROP_ALPHA_V1",
          "stages": [
            "every_accepted_state"
          ]
        },
        {
          "id": "free_dest",
          "type": "distribution",
          "unit": "dimensionless",
          "clause": "C2",
          "objects": [
            "FC"
          ],
          "mode": "free",
          "stages": [
            "every_accepted_state"
          ]
        },
        {
          "id": "sum",
          "type": "input_sum",
          "unit": "MW",
          "clause": "C3",
          "objects": [
            "FA",
            "FB",
            "FC",
            "FD"
          ],
          "target": {
            "op": "baseline_sum",
            "state": "fictional_base",
            "quantity": "plini",
            "objects": [
              "FA",
              "FB",
              "FC",
              "FD"
            ]
          },
          "accuracy": "P_SUM_V1",
          "stages": [
            "every_accepted_state"
          ]
        },
        {
          "id": "qp",
          "type": "qp_policy",
          "unit": "Mvar",
          "clause": "C4",
          "objects": [
            "FA",
            "FB",
            "FC",
            "FD"
          ],
          "state": "fictional_base",
          "policy": "each_baseline_ratio",
          "accuracy": "QP_RESIDUAL_V1",
          "stages": [
            "every_accepted_state"
          ]
        },
        {
          "id": "lock",
          "type": "fixed_inputs",
          "unit": "per_field",
          "clause": "C5",
          "objects": [
            "FD"
          ],
          "state": "fictional_base",
          "fields": [
            "plini",
            "qlini"
          ],
          "accuracy": "FIXED_EXACT_V1",
          "stages": [
            "every_accepted_state"
          ]
        },
        {
          "id": "limits",
          "type": "alpha_bounds",
          "unit": "dimensionless",
          "clause": "C5",
          "objects": [
            "FA",
            "FB",
            "FC",
            "FD"
          ],
          "lower": 0.99,
          "upper": 1.02,
          "precision": "ALPHA_READ_V1",
          "stages": [
            "every_accepted_state"
          ]
        },
        {
          "id": "volts",
          "type": "voltage_bounds",
          "unit": "pu",
          "clause": "C6",
          "objects": [
            "FX",
            "FY"
          ],
          "bounds": {
            "kind": "baseline_band",
            "state": "fictional_base",
            "lower_offset": -0.01,
            "upper_offset": 0.02
          },
          "precision": "VOLTAGE_EDGE_ZERO_V1",
          "stages": [
            "every_accepted_state"
          ]
        }
      ],
      "preserve": {
        "other_load_inputs": true,
        "topology": true,
        "control_settings": true,
        "flow_settings": true
      }
    },
    "plan": {
      "operation": "solve",
      "selected": [
        "FA",
        "FB",
        "FC"
      ],
      "reason": "fictional example: proportional source, free destination, FD fixed"
    }
  },
  "example_context": {
    "origin": "independent fictional syntax fixture, no actual-task gold/solution",
    "catalog": {
      "FA": {
        "kind": "load",
        "path": "fictional::FA",
        "base_inputs": {
          "plini": 40.0,
          "qlini": 12.0
        }
      },
      "FB": {
        "kind": "load",
        "path": "fictional::FB",
        "base_inputs": {
          "plini": 20.0,
          "qlini": 2.0
        }
      },
      "FC": {
        "kind": "load",
        "path": "fictional::FC",
        "base_inputs": {
          "plini": 15.0,
          "qlini": 3.0
        }
      },
      "FD": {
        "kind": "load",
        "path": "fictional::FD",
        "base_inputs": {
          "plini": 5.0,
          "qlini": 1.0
        }
      },
      "FX": {
        "kind": "voltage",
        "path": "fictional::FX",
        "baseline_voltage_pu": 1.03
      },
      "FY": {
        "kind": "voltage",
        "path": "fictional::FY",
        "baseline_voltage_pu": 0.95
      }
    },
    "snapshot": {
      "state_id": "fictional_base",
      "quantities": {
        "FA": {
          "plini": 40.0,
          "qlini": 12.0
        },
        "FB": {
          "plini": 20.0,
          "qlini": 2.0
        },
        "FC": {
          "plini": 15.0,
          "qlini": 3.0
        },
        "FD": {
          "plini": 5.0,
          "qlini": 1.0
        },
        "FX": {
          "voltage_pu": 1.03
        },
        "FY": {
          "voltage_pu": 0.95
        }
      }
    },
    "policies": {
      "version": "precision-policy-v1",
      "policies": {
        "P_SUM_V1": {
          "unit": "MW",
          "user_allowed_error": 2e-05,
          "effective_evaluation_tolerance": 2e-05,
          "storage_policy": "existing preregistered float32 budget",
          "extra_storage_error_added": 0.0,
          "solver_policy": "retained-active-face-v1.1",
          "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
        },
        "QP_RESIDUAL_V1": {
          "unit": "Mvar",
          "user_allowed_error": 1e-05,
          "effective_evaluation_tolerance": 1e-05,
          "storage_policy": "existing preregistered float32 budget",
          "extra_storage_error_added": 0.0,
          "solver_policy": "retained-active-face-v1.1",
          "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
        },
        "ALPHA_READ_V1": {
          "unit": "dimensionless",
          "user_allowed_error": 1e-07,
          "effective_evaluation_tolerance": 1e-07,
          "storage_policy": "existing readback/exact-bound policy",
          "extra_storage_error_added": 0.0,
          "solver_policy": "retained-active-face-v1.1",
          "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
        },
        "FIXED_EXACT_V1": {
          "unit": "per_field",
          "user_allowed_error": 0.0,
          "effective_evaluation_tolerance": 0.0,
          "storage_policy": "existing readback/exact-bound policy",
          "extra_storage_error_added": 0.0,
          "solver_policy": "retained-active-face-v1.1",
          "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
        },
        "VOLTAGE_EDGE_ZERO_V1": {
          "unit": "pu",
          "user_allowed_error": 0.0,
          "effective_evaluation_tolerance": 0.0,
          "storage_policy": "existing readback/exact-bound policy",
          "extra_storage_error_added": 0.0,
          "solver_policy": "retained-active-face-v1.1",
          "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
        },
        "PROP_ALPHA_V1": {
          "unit": "dimensionless",
          "user_allowed_error": 1e-07,
          "effective_evaluation_tolerance": 1e-07,
          "storage_policy": "existing readback/exact-bound policy",
          "extra_storage_error_added": 0.0,
          "solver_policy": "retained-active-face-v1.1",
          "solver_relation_check": "1e-10*max(1,abs(b)) equalities; 1e-12*max(1,abs(b)) inequalities; not added to user acceptance"
        }
      },
      "rule": "User allowed deviation, storage uncertainty and numerical residual checks are distinct. Existing user budget already includes its preregistered storage allowance; never add it twice."
    },
    "allowed": [
      "FA",
      "FB",
      "FC"
    ],
    "original_requirements": "最终完成转移。其余条件在每个接受状态满足。"
  },
  "execution_settings": {
    "mode": "compile_only",
    "not_an_electrical_requirement": true,
    "plan_intent": "Use solve when proposing construction even in compile_only mode. Use stop only to request no solve; selected must then be empty."
  },
  "shared_public_information": {
    "load_sets": {
      "source": [
        "L2",
        "L3",
        "L5"
      ],
      "destination": [
        "L1",
        "L4",
        "L6"
      ]
    },
    "balance_policy": {
      "id": "MODEL_REFERENCE_BOUNDS_V1",
      "rule": "Keep frozen controls; require one exposed reference flag and finite, readable effective model P/Q bounds; independently check actual output. No unlimited slack assumption.",
      "verification": "read-only baseline model bounds and same preserved reference-flag mechanism",
      "bounds": {
        "name": "G 65",
        "Pmin_MW": 0.0,
        "Pmax_MW": 1000.0,
        "Qmin_Mvar": -67.0,
        "Qmax_Mvar": 200.0
      }
    },
    "scenario_criteria": {
      "id": "DEVELOPMENT_VOLTAGE_STRESS_V1",
      "source": "本包在D和模型输出前预登记的受控稳态电压变化研究判据；不是行业安全阈值、严重低电压或稳定裕度标准。模型vlmin/vlmax仅作背景诊断。",
      "bands_delta_pu": {
        "WS_TARGET": [
          -0.0035,
          -0.0025
        ],
        "SMYTHE_TARGET_A": [
          -0.0015,
          -0.00075
        ],
        "SMYTHE_TARGET_B": [
          -0.0028,
          -0.0018
        ]
      },
      "reason": "在既有不超过20%的增长域内检验毫pu量级的受控电压应力及相邻观察量保持。数值在本包搜索前固定，不从本包候选倍率反推，不根据组别表现调带。"
    },
    "reference_state_id": "base_v1",
    "policy_id": "PQ_ALPHA_TECHNICAL_V1",
    "object_actuator_bounds": {
      "L1": {
        "lower": 0.99,
        "upper": 1.02
      },
      "L2": {
        "lower": 0.99,
        "upper": 1.02
      },
      "L3": {
        "lower": 0.99,
        "upper": 1.02
      },
      "L4": {
        "lower": 0.99,
        "upper": 1.02
      },
      "L5": {
        "lower": 0.99,
        "upper": 1.02
      },
      "L6": {
        "lower": 0.99,
        "upper": 1.02
      }
    },
    "fixed_actuator_semantics": "Objects not selected for variables remain baseline-fixed. Statistical constraint sets may include fixed objects.",
    "shared_tools": "State value/sum, scalar multiplication, per-object voltage offsets, joint bounded numerical solve. No manual continuous multipliers required.",
    "execution": "This batch compiles and solves offline only; this is not a physical demand and does not require stop."
  }
}
```
