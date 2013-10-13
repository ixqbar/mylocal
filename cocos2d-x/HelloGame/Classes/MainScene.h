
#ifndef _GAME_OVER_SCENE_H_
#define _GAME_OVER_SCENE_H_

#include "cocos2d.h"
#include "cocos-ext.h"
#include "JsonBox.h"
#include "LSLog.h"

USING_NS_CC;
USING_NS_CC_EXT;

class MainScene:public cocos2d::CCLayer,
public CCBMemberVariableAssigner,//绑定响应的成员变量
public CCNodeLoaderListener,     //加载节点响应回调
public CCBSelectorResolver       //按钮控件响应回调
{

private:
    CCLabelTTF *mLabelText;
    
public:
    MainScene();
    ~MainScene();
    static CCScene* scene();
    CCB_STATIC_NEW_AUTORELEASE_OBJECT_WITH_INIT_METHOD(MainScene, create);
    
    void onRequestFinished(CCHttpClient* client, CCHttpResponse* response);
    void onButtonClicked(CCObject *pSender, CCControlEvent pCCControlEvent);
    void onMenuClicked(CCObject *pSender);
    
    virtual bool onAssignCCBMemberVariable(CCObject* pTarget, const char* pMemberVariableName, CCNode* pNode);
    virtual bool onAssignCCBCustomProperty(CCObject* pTarget, const char* pMemberVariableName, CCBValue* pCCBValue);

    virtual void onNodeLoaded(CCNode * pNode, CCNodeLoader * pNodeLoader);
    
    virtual SEL_MenuHandler onResolveCCBCCMenuItemSelector(CCObject * pTarget, const char* pSelectorName);
    virtual SEL_CallFuncN onResolveCCBCCCallFuncSelector(CCObject * pTarget, const char* pSelectorName);
    virtual SEL_CCControlHandler onResolveCCBCCControlSelector(CCObject * pTarget, const char* pSelectorName);
        
};

class MainSceneLoad:public CCLayerLoader {
    
public:
    CCB_STATIC_NEW_AUTORELEASE_OBJECT_METHOD(MainSceneLoad, loader);
protected:
    CCB_VIRTUAL_NEW_AUTORELEASE_CREATECCNODE_METHOD(MainScene);
};

#endif // _GAME_OVER_SCENE_H_
