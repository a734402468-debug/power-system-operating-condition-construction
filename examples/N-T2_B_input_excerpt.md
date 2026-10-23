# N-T2: basic expression input

Extract from the recorded input. Record-identification fields are omitted and JSON is indented for readability; electrical requirements, supplied numerical values, instructions, and syntax examples are retained. The two forms use different instructions and examples, as discussed in Supplementary Section S4.

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
    "protocol": "shared-stage-set-v1.1/T/optional-provenance-v1",
    "root_required_only": [
      "baseline_state",
      "variables",
      "calls",
      "preserve",
      "plan"
    ],
    "root_instruction": "These fields are directly at the output root; no decision wrapper.",
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
    "variables": {
      "objects": "nonempty unique authorized load ID array",
      "mapping": "baseline_PQ_times_absolute_alpha"
    },
    "calls": {
      "shape": "array of explicit tool calls; batching is allowed in one answer",
      "constraint_call_required_only": [
        "id",
        "tool",
        "type",
        "objects",
        "values",
        "unit",
        "policy",
        "clause",
        "each",
        "stages"
      ],
      "tool": "ONE string constraint",
      "types": {
        "input_sum_delta": {
          "role": "load",
          "unit": "MW",
          "values_required_only": [
            "delta"
          ],
          "policy": "P_SUM_V1"
        },
        "active_power_sum": {
          "role": "load",
          "unit": "MW",
          "values_required_only": [
            "value"
          ],
          "policy": "P_SUM_V1"
        },
        "baseline_qp": {
          "role": "load",
          "unit": "Mvar",
          "values_required_only": [],
          "policy": "QP_RESIDUAL_V1"
        },
        "alpha_bounds": {
          "role": "load",
          "unit": "dimensionless",
          "values_required_only": [
            "lower",
            "upper"
          ],
          "policy": "ALPHA_READ_V1"
        },
        "fixed_parameter": {
          "role": "load",
          "unit": "MW for plini; Mvar for qlini",
          "values_required_only": [
            "field",
            "value"
          ],
          "policy": "FIXED_EXACT_V1"
        },
        "voltage_bounds": {
          "role": "voltage",
          "unit": "pu",
          "values_required_only": [
            "lower",
            "upper"
          ],
          "policy": "VOLTAGE_EDGE_ZERO_V1"
        },
        "proportional_change": {
          "role": "load",
          "unit": "dimensionless",
          "values_required_only": [],
          "policy": "PROP_ALPHA_V1"
        }
      },
      "free_call_required_only": [
        "id",
        "tool",
        "objects",
        "clause",
        "stages"
      ],
      "free_tool": "ONE string free_allocation; no equation or numeric tolerance",
      "each": "boolean. true explicitly iterates objects and substitutes $object in expressions; fixed_parameter and voltage_bounds require one object per constructed row (use each:true for a batch).",
      "values": "finite numbers or typed expressions; fixed_parameter.field is ONE string plini/qlini. baseline_qp/proportional_change values is {}.",
      "clause": "ONE source tag C1..C7 chosen to cite original text; does not certify semantics",
      "id": "unique nonempty string",
      "stages": {
        "type": "array",
        "items": "ONE string: baseline | every_accepted_state | final",
        "min_items": 1,
        "unique": true
      }
    },
    "state_arithmetic": {
      "literal": [
        "op=literal",
        "value=number",
        "unit=MW/Mvar/pu/dimensionless"
      ],
      "baseline_sum": [
        "op=baseline_sum",
        "state=baseline ID",
        "quantity=plini/qlini",
        "objects=load ID array"
      ],
      "baseline_value": [
        "op=baseline_value",
        "state=baseline ID",
        "quantity=plini/qlini/voltage_pu",
        "object=exact ID"
      ],
      "scale": [
        "op=scale",
        "factor=number",
        "base=expression"
      ],
      "minimum": [
        "op=minimum",
        "items=array of 2..4 expressions of identical units"
      ],
      "offset": [
        "op=offset",
        "base=typed expression",
        "value=number in SAME unit; result=base+value"
      ]
    },
    "baseline_state": "supplied state_id; baseline_qp uses this explicit reference",
    "preserve": {
      "other_load_inputs": "required boolean",
      "topology": "required boolean",
      "control_settings": "required boolean",
      "flow_settings": "required boolean"
    },
    "plan": {
      "operation": "ONE solve/stop string",
      "selected": "unique authorized load ID array (empty for stop)",
      "reason": "short string"
    },
    "semantics": [
      "input_sum_delta explicitly constructs SUM(plini) - its OWN baseline SUM = delta. Add source and destination relations yourself; no automatic transfer macro.",
      "active_power_sum explicitly constructs SUM(plini)=value. baseline_sum reads exactly the supplied object set.",
      "baseline_qp preserves EACH listed load own baseline ratio; the shared numeric kernel performs the ratio arithmetic.",
      "proportional_change explicitly enforces equal multipliers for its set; free_allocation adds NO equation.",
      "Fixed inputs: add separate fixed_parameter calls for plini and qlini. Values may read baseline_value of $object with each:true.",
      "Voltage bands: add voltage_bounds calls with explicit lower and upper expressions. offset(baseline_value(voltage_pu), offset) computes each bus own interval.",
      "All rows enter the SAME bounded solver, actual evaluator and stage rules as F. No generated Python or hidden requirement completion.",
      "Mechanical internal schema version is wrapped by program. This is NOT the F declarative specification/transfer expander."
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
    "baseline_state": "fictional_base",
    "variables": {
      "objects": [
        "FA",
        "FB",
        "FC"
      ],
      "mapping": "baseline_PQ_times_absolute_alpha"
    },
    "calls": [
      {
        "id": "move_out",
        "tool": "constraint",
        "type": "input_sum_delta",
        "objects": [
          "FA",
          "FB"
        ],
        "values": {
          "delta": {
            "op": "scale",
            "factor": -1,
            "base": {
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
            }
          }
        },
        "unit": "MW",
        "policy": "P_SUM_V1",
        "clause": "C1",
        "each": false,
        "stages": [
          "final"
        ]
      },
      {
        "id": "move_in",
        "tool": "constraint",
        "type": "input_sum_delta",
        "objects": [
          "FC"
        ],
        "values": {
          "delta": {
            "op": "scale",
            "factor": 1,
            "base": {
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
            }
          }
        },
        "unit": "MW",
        "policy": "P_SUM_V1",
        "clause": "C1",
        "each": false,
        "stages": [
          "final"
        ]
      },
      {
        "id": "equal_source",
        "tool": "constraint",
        "type": "proportional_change",
        "objects": [
          "FA",
          "FB"
        ],
        "values": {},
        "unit": "dimensionless",
        "policy": "PROP_ALPHA_V1",
        "clause": "C2",
        "each": false,
        "stages": [
          "every_accepted_state"
        ]
      },
      {
        "id": "free_dest",
        "tool": "free_allocation",
        "objects": [
          "FC"
        ],
        "clause": "C2",
        "stages": [
          "every_accepted_state"
        ]
      },
      {
        "id": "sum",
        "tool": "constraint",
        "type": "active_power_sum",
        "objects": [
          "FA",
          "FB",
          "FC",
          "FD"
        ],
        "values": {
          "value": {
            "op": "baseline_sum",
            "state": "fictional_base",
            "quantity": "plini",
            "objects": [
              "FA",
              "FB",
              "FC",
              "FD"
            ]
          }
        },
        "unit": "MW",
        "policy": "P_SUM_V1",
        "clause": "C3",
        "each": false,
        "stages": [
          "every_accepted_state"
        ]
      },
      {
        "id": "qp",
        "tool": "constraint",
        "type": "baseline_qp",
        "objects": [
          "FA",
          "FB",
          "FC",
          "FD"
        ],
        "values": {},
        "unit": "Mvar",
        "policy": "QP_RESIDUAL_V1",
        "clause": "C4",
        "each": false,
        "stages": [
          "every_accepted_state"
        ]
      },
      {
        "id": "lock_plini",
        "tool": "constraint",
        "type": "fixed_parameter",
        "objects": [
          "FD"
        ],
        "values": {
          "field": "plini",
          "value": {
            "op": "baseline_value",
            "state": "fictional_base",
            "quantity": "plini",
            "object": "$object"
          }
        },
        "unit": "MW",
        "policy": "FIXED_EXACT_V1",
        "clause": "C5",
        "each": true,
        "stages": [
          "every_accepted_state"
        ]
      },
      {
        "id": "lock_qlini",
        "tool": "constraint",
        "type": "fixed_parameter",
        "objects": [
          "FD"
        ],
        "values": {
          "field": "qlini",
          "value": {
            "op": "baseline_value",
            "state": "fictional_base",
            "quantity": "qlini",
            "object": "$object"
          }
        },
        "unit": "Mvar",
        "policy": "FIXED_EXACT_V1",
        "clause": "C5",
        "each": true,
        "stages": [
          "every_accepted_state"
        ]
      },
      {
        "id": "limits",
        "tool": "constraint",
        "type": "alpha_bounds",
        "objects": [
          "FA",
          "FB",
          "FC",
          "FD"
        ],
        "values": {
          "lower": 0.99,
          "upper": 1.02
        },
        "unit": "dimensionless",
        "policy": "ALPHA_READ_V1",
        "clause": "C5",
        "each": false,
        "stages": [
          "every_accepted_state"
        ]
      },
      {
        "id": "volts",
        "tool": "constraint",
        "type": "voltage_bounds",
        "objects": [
          "FX",
          "FY"
        ],
        "values": {
          "lower": {
            "op": "offset",
            "base": {
              "op": "baseline_value",
              "state": "fictional_base",
              "quantity": "voltage_pu",
              "object": "$object"
            },
            "value": -0.01
          },
          "upper": {
            "op": "offset",
            "base": {
              "op": "baseline_value",
              "state": "fictional_base",
              "quantity": "voltage_pu",
              "object": "$object"
            },
            "value": 0.02
          }
        },
        "unit": "pu",
        "policy": "VOLTAGE_EDGE_ZERO_V1",
        "clause": "C6",
        "each": true,
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
