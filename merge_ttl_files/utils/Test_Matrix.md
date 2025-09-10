Tests have been done with graphs ttl files generated the 4th of September by modifying the treated files for REMAIN_OCC=4 in order to correspond to all the different possible cases


| dup_occ = REMAIN_OCC        |   Remain_occ        |   Result            |  Comment                                      |
|:---------------------------:|:-------------------:|:-------------------:|:---------------------------------------------:|
|dup_occ_treated              |EQUAL                |      test OK        |Normal behavior                                |
|dup_occ_treated              |HIGHER THAN          |      test OK        |Abnormal behavior should be equal to REMAIN OCC|
|dup_occ_treated              |LOWER THAN           |      test OK        |AbNormal behavior should be equal to REMAIN OCC|


| dup_occ higher than REMAIN_OCC        |   Remain_occ        |   Result            |  Comment                                      |
|:-------------------------------------:|:-------------------:|:-------------------:|:---------------------------------------------:|
|dup_occ_treated                        |EQUAL                |      test OK        |Normal behavior                                |
|dup_occ_treated                        |HIGHER THAN          |      test OK        |Abnormal behavior should be equal to REMAIN OCC|
|dup_occ_treated                        |LOWER THAN           |      test OK        |Abnormal behavior should be equal to REMAIN OCC|


| dup_occ lower than REMAIN_OCC        |   Remain_occ        |   Result            |   Comment                                  |
|:------------------------------------:|:-------------------:|:-------------------:|:------------------------------------------:|
|dup_occ_treated                       |EQUAL                |       test OK       |Abnormal behavior should be equal to dup_occ|
|dup_occ_treated                       |HIGHER THAN          |       test OK       |Abnormal behavior should be equal to dup_occ|
|dup_occ_treated                       |LOWER THAN           |       test OK       |Abnormal behavior should be equal to dup_occ|

| dup_occ lower than REMAIN_OCC        |   dup_occ           |   Result            |   Comment      |
|dup_occ_treated                       |EQUAL                |       test OK       |Normal behavior |
