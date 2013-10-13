LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := cocos2dcpp_shared

LOCAL_MODULE_FILENAME := libcocos2dcpp

LOCAL_SRC_FILES := hellocpp/main.cpp \
                   ../../Classes/AppDelegate.cpp \
                   ../../Classes/HelloWorldScene.cpp \
                   ../../Classes/MainScene.cpp \
                   ../../libs/JsonBox/src/Array.cpp \
				   ../../libs/JsonBox/src/Convert.cpp \
				   ../../libs/JsonBox/src/Escaper.cpp \
				   ../../libs/JsonBox/src/IndentCanceller.cpp \
				   ../../libs/JsonBox/src/Indenter.cpp \
				   ../../libs/JsonBox/src/Object.cpp \
				   ../../libs/JsonBox/src/SolidusEscaper.cpp \
				   ../../libs/JsonBox/src/Value.cpp \
				   ../../libs/LSLog/LSLog.cpp

LOCAL_C_INCLUDES := $(LOCAL_PATH)/../../Classes \
					$(LOCAL_PATH)/../../libs/JsonBox/include \
					$(LOCAL_PATH)/../../libs/LSLog

LOCAL_WHOLE_STATIC_LIBRARIES += cocos2dx_static
LOCAL_WHOLE_STATIC_LIBRARIES += cocosdenshion_static
LOCAL_WHOLE_STATIC_LIBRARIES += box2d_static
LOCAL_WHOLE_STATIC_LIBRARIES += chipmunk_static
LOCAL_WHOLE_STATIC_LIBRARIES += cocos_extension_static

LOCAL_CFLAGS += -DCOCOS2D_DEBUG=1 

include $(BUILD_SHARED_LIBRARY)

$(call import-module,cocos2dx)
$(call import-module,cocos2dx/platform/third_party/android/prebuilt/libcurl)
$(call import-module,CocosDenshion/android)
$(call import-module,extensions)
$(call import-module,external/Box2D)
$(call import-module,external/chipmunk)
