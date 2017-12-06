# -*- coding: utf-8 -*-
# Change columns/row
def changeIndexFromTo(from_index, to_index):
    global matrix_ordered
    global diputados_list_reordered
    
    # change list index position
    diputados_list_reordered[to_index], diputados_list_reordered[from_index] = diputados_list_reordered[from_index], diputados_list_reordered[to_index]

    # change columns position
    matrix_ordered[:,from_index], matrix_ordered[:,to_index] = matrix_ordered[:,to_index], matrix_ordered[:,from_index].copy()
    
    # change rows position
    matrix_ordered[from_index,:], matrix_ordered[to_index,:] = matrix_ordered[to_index,:], matrix_ordered[from_index,:].copy()


def bottomUpLeftToRightBigToSmall(threshold = 0, cut = 120):
    for rep in range(0,120):
        count_changes = 0
        rep_back = 119 - rep
        while True:
            for i in range(0, 119):
                if i > rep_back and i < rep_back + cut:
                    # Compare with element on the right
                    if matrix_ordered[rep_back,i] + threshold < matrix_ordered[rep_back,i+1]:
                        count_changes = count_changes + 1
                        changeIndexFromTo(i,i+1)
            
            if count_changes == 0:
                break
            else:
                count_changes = 0

def upBottomLeftToRightBigToSmall(threshold = 0, cut = 120):
    for rep in range(0, 120):
        count_changes = 0
        while True:
            for i in range(0, 119):
                if i > rep and i < rep + cut:
                    # Compare with element on the right
                    if matrix_ordered[rep,i] + threshold < matrix_ordered[rep,i+1]:
                        count_changes = count_changes + 1
                        changeIndexFromTo(i,i+1)
            
            if count_changes == 0:
                break
            else:
                count_changes = 0

def bottomUpLeftToRightSmallToBig(threshold = 0, cut = 120):
    for rep in range(0,120):
        count_changes = 0
        rep_back = 119 - rep
        while True:
            for i in range(0, 119):
                if i < rep_back and i > rep_back - cut:
                    # Compare with element on the right
                    if matrix_ordered[rep_back,i] - threshold > matrix_ordered[rep_back,i+1]:
                        count_changes = count_changes + 1
                        changeIndexFromTo(i,i+1)
            
            if count_changes == 0:
                break
            else:
                count_changes = 0
            
def upBottomLeftToRightSmallToBig(threshold = 0, cut = 120):
    for rep in range(0,120):
        count_changes = 0
        while True:
            for i in range(0, 120):
                if i < rep and i > rep - cut:
                    # Compare with element on the right
                    if matrix_ordered[rep,i] - threshold > matrix_ordered[rep,i+1]:
                        count_changes = count_changes + 1
                        changeIndexFromTo(i,i+1)
            
            if count_changes == 0:
                break
            else:
                count_changes = 0
"""
bottomUpLeftToRightBigToSmall()
#upBottomLeftToRightBigToSmall()
#bottomUpLeftToRightSmallToBig()
upBottomLeftToRightSmallToBig(threshold = 20)
bottomUpLeftToRightSmallToBig(threshold = 20)
"""