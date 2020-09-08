def convertScheduleRecord(schedule_record):
    ganttList = []
    #keyList = list(schedule_record.keys())
    keyList = [
            'LD_1_WAIT_ID',
            'LD_1_ID',
            'LD_2_ID',
            'BA_ID',
            'FINERY_1_ID',
            'FINERY_2_ID',
            'FINERY_3_ID',
            'FINERY_4_ID',
            'CAST_1_WAIT_ID',
            'CAST_1_ID',
            'CAST_2_ID'] 
    
    Job = schedule_record['PONO']
    for i in range(len(keyList)):
        pos = keyList[i].find('_ID')
        if  pos!=-1 and schedule_record[keyList[i]]!='' :
            valueMachine = schedule_record[keyList[i]]
            valueStartTime = schedule_record[keyList[i][:pos]+'_START_TIME']
            valueFinishTime = schedule_record[keyList[i][:pos]+'_END_TIME']
            ganttList.append(dict(Task = valueMachine, Start = valueStartTime, Finish = valueFinishTime, Resource = Job ))
    return ganttList

def json2dict(schedule_result):
    ganttData = []
    for i in range(0,len(schedule_result)):
        schedule_record = schedule_result[i]
        record = convertScheduleRecord(schedule_record)
        ganttData = ganttData+record
        
    return ganttData

#ganttData = json2dict(schedule_result)

# =============================================================================
# result={
#             "PLAN_SAVE_TIME" : "",
#             "PONO" : "",
#             "HTNO" : 330351,
#             "SG" : "",
#             "FINERY_PATH_ID" : "",
#             "LD_1_WAIT_ID" : "",
#             "LD_1_ID" : "",
#             "LD_2_ID" : "",
#             "STOVE_PROCESS_NO" : "",
#             "P_PROCESS_NO" : "",
#             "BA_ID" : "203",
#             "FINERY_1_ID" : "",
#             "FINERY_2_ID" : "",
#             "FINERY_3_ID" : "",
#             "FINERY_4_ID" : "",
#             "FINERY_1_PROCESS_NO" : "",
#             "FINERY_2_PROCESS_NO" : "",
#             "FINERY_3_PROCESS_NO" : "",
#             "FINERY_4_PROCESS_NO" : "",
#             "CAST_1_WAIT_ID" : "",
#             "CAST_1_ID" : "",
#             "CAST_2_ID" : "",
#             "CAST_1_PROCESS_NO" : "",
#             "CASTNO_POUR" : "",
#             "INGOT_TYPE" : "",
#             "INGOT_COU" : 2,
#             "LD_1_WAIT_START_TIME" : "",
#             "LD_1_WAIT_END_TIME" : "",
#             "LD_1_START_TIME" : "",
#             "LD_1_BLOW_END_TIME" : "",
#             "LD_1_TAPPING_START_TIME" : "",
#             "LD_1_END_TIME" : "",
#             "LD_2_WAIT_START_TIME" : "",
#             "LD_2_WAIT_END_TIME" : "",
#             "LD_2_START_TIME" : "",
#             "LD_2_BLOW_END_TIME" : "",
#             "LD_2_TAPPING_START_TIME" : "",
#             "LD_2_END_TIME" : "",
#             "BA_START_TIME" : "",
#             "BA_END_TIME" : "",
#             "FINERY_1_START_TIME" : "",
#             "FINERY_1_END_TIME" : "",
#             "FINERY_2_START_TIME" : "",
#             "FINERY_2_END_TIME" : "",
#             "FINERY_3_START_TIME" : "",
#             "FINERY_3_END_TIME" : "",
#             "FINERY_4_START_TIME" : "",
#             "FINERY_4_END_TIME" : "",
#             "CAST_1_WAIT_START_TIME" : "",
#             "CAST_1_WAIT_END_TIME" : "",
#             "CAST_1_START_TIME" : "",
#             "CAST_1_END_TIME" : "",
#             "CAST_2_START_TIME" : "",
#             "CAST_2_END_TIME" : "",
#             "CAST_TYPE" : 1,
#             "PLAN_SOURCE" : 1,
#             "PLAN_STYLE" : 1,
#             "PLAN_STATUS" : 6,
#             "LADLE_STATUS" : "",
#             "DETAILS" : "",
#             "D_ARRIVE_TURN_TIME" : "",
#             "D_REAL_STATUS_ID" : "",
#             "D_STATUS_TIME" : "",
#             "D_TIME_SUBTRACT" : "",
#             "D_DECISION_SG" : "",
#             "D_RETURN_ID" : "",
#             "D_DISTURB_TIME" : "",
#             "D_DISTURB_TEMP" : "",
#             "D_DISTURB_CC" : "",
#             "D_DISTURB_SG" : "",
#             "D_DISTURB_DEVICE" : "",
#             "D_DISTURB_OTHERS" : "",
#             "D_FIRST_STRATEGY_TIME" : "",
#             "D_FIRST_SIMILARITY_TIME" : "",
#             "D_SECOND_STRATEGY_TIME" : "",
#             "D_SECOND_SIMILARITY_TIME" : "",
#             "D_THIRD_STRATEGY_TIME" : "",
#             "D_THIRD_SIMILARITY_TIME" : "",
#             "D_FIRST_STRATEGY_TEMP" : "",
#             "D_FIRST_SIMILARITY_TEMP" : "",
#             "D_SECOND_STRATEGY_TEMP" : "",
#             "D_SECOND_SIMILARITY_TEMP" : "",
#             "D_THIRD_STRATEGY_TEMP" : "",
#             "D_THIRD_SIMILARITY_TEMP" : "",
#             "D_FIRST_STRATEGY_CC" : "",
#             "D_FIRST_SIMILARITY_CC" : "",
#             "D_SECOND_STRATEGY_CC" : "",
#             "D_SECOND_SIMILARITY_CC" : "",
#             "D_THIRD_STRATEGY_CC" : "",
#             "D_THIRD_SIMILARITY_CC" : "",
#             "OPTIMIZATION_STYLE" : "",
#             "CC_IDENTIFY" : "",
#             "ROWID" : "AAANHaAAGAAAANWAAA"}*/
# =============================================================================
