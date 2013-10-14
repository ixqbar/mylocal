#include "MainScene.h"

USING_NS_CC;
USING_NS_CC_EXT;

MainScene::MainScene():mLabelText(NULL)
{
    
}

MainScene::~MainScene()
{
    CC_SAFE_RELEASE_NULL(mLabelText);
}

CCScene* MainScene::scene()
{
    CCScene *scene = CCScene::create();
    
    CCNodeLoaderLibrary* ccNodeLoaderLibrary = CCNodeLoaderLibrary::sharedCCNodeLoaderLibrary();
    ccNodeLoaderLibrary->registerCCNodeLoader("MainScene", MainSceneLoad::loader());
    
    CCBReader* ccbReader = new CCBReader(ccNodeLoaderLibrary);
    CCNode* node = ccbReader->readNodeGraphFromFile("MainScene.ccbi", scene);
    ccbReader->autorelease();
    
    if (node!=NULL) {
        node->setTag(100);
        scene->addChild(node);
    }
    
    return scene;
}

void MainScene::onRequestFinished(CCHttpClient* client, CCHttpResponse* response)
{
    LSLog::info("todo=%s", "hello");
    LOG_INFO("ok=%d,%s", 1, "wang");
    CCLOG("request tag=%s, response code=%d", response->getHttpRequest()->getTag(), response->getResponseCode());
    if (!response->isSucceed()) {
        this->mLabelText->setString("网络错误");
        return;
    }
    
    std::vector<char> *buffer = response->getResponseData();
    std::string content(buffer->begin(), buffer->end());
    CCLOG("response content=%s", content.c_str());
    
    JsonBox::Value val;
    val.loadFromString(content);
    
    this->mLabelText->setString(val["result"].getString().c_str());
}

void MainScene::onButtonClicked(CCObject *pSender, CCControlEvent pCCControlEvent)
{
    LOG_INFO("clicked!");
    CCDirector::sharedDirector()->replaceScene(HelloWorld::scene());
}

void MainScene::onMenuClicked(CCObject *pSender)
{
    this->mLabelText->setString("^_^");
}

bool MainScene::onAssignCCBMemberVariable(CCObject *pTarget, const char *pMemberVariableName, CCNode *pNode)
{
    CCB_MEMBERVARIABLEASSIGNER_GLUE(this, "mLabelText", CCLabelTTF*, this->mLabelText);
    
    return true;
}

bool MainScene::onAssignCCBCustomProperty(CCObject *pTarget, const char *pMemberVariableName, CCBValue *pCCBValue)
{
    return true;
}

void MainScene::onNodeLoaded(CCNode *pNode, CCNodeLoader *pNodeLoader)
{
    CCHttpRequest *request = new CCHttpRequest();
    request->setUrl("http://xingqiba.sinaapp.com/test.php");
    request->setRequestType(CCHttpRequest::kHttpGet);
    request->setTag("todo");
    request->setResponseCallback(this, httpresponse_selector(MainScene::onRequestFinished));
    
    CCHttpClient *client = CCHttpClient::getInstance();
    client->setTimeoutForConnect(30);
    client->setTimeoutForRead(30);
    client->send(request);
    
    request->release();
}

SEL_MenuHandler MainScene::onResolveCCBCCMenuItemSelector(CCObject * pTarget, const char* pSelectorName)
{
    CCB_SELECTORRESOLVER_CCMENUITEM_GLUE(this, "onMenuClicked", MainScene::onMenuClicked);
    return NULL;
}

SEL_CallFuncN MainScene::onResolveCCBCCCallFuncSelector(CCObject * pTarget, const char* pSelectorName)
{
    return NULL;
}

SEL_CCControlHandler MainScene::onResolveCCBCCControlSelector(CCObject * pTarget, const char* pSelectorName)
{
    CCB_SELECTORRESOLVER_CCCONTROL_GLUE(this, "onButtonClicked", MainScene::onButtonClicked);
    return NULL;
}





