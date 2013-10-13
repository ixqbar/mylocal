#include "AppDelegate.h"
#include "MainScene.h"

USING_NS_CC;

AppDelegate::AppDelegate()
{
}

AppDelegate::~AppDelegate() 
{
}

bool AppDelegate::applicationDidFinishLaunching() {
    // initialize director
    CCDirector* pDirector = CCDirector::sharedDirector();
    CCEGLView* pEGLView = CCEGLView::sharedOpenGLView();
    
    pDirector->setOpenGLView(pEGLView);
	
    // turn on display FPS
    pDirector->setDisplayStats(true);
    
    // set FPS. the default value is 1.0/60 if you don't call this
    pDirector->setAnimationInterval(1.0 / 60);
    
    
//    CCSize frameSize = pEGLView->getFrameSize();
//    // 设置 LsSize 固定值
//    CCSize lsSize = CCSizeMake(480, 320);
//    
//    float scaleX = (float) frameSize.width / lsSize.width;
//    float scaleY = (float) frameSize.height / lsSize.height;
//    
//    // 定义 scale 变量
//    float scale = 0.0f; // MAX(scaleX, scaleY);
//    if (scaleX > scaleY) {
//        // 如果是 X 方向偏大，那么 scaleX 需要除以一个放大系数，放大系数可以由枞方向获取，
//        // 因为此时 FrameSize 和 LsSize 的上下边是重叠的
//        scale = scaleX / (frameSize.height / (float) lsSize.height);
//    } else {
//        scale = scaleY / (frameSize.width / (float) lsSize.width);
//    }
//    
//    CCLog("x: %f; y: %f; scale: %f", scaleX, scaleY, scale);
//    
//    // 根据 LsSize 和屏幕宽高比动态设定 WinSize
//    pEGLView->setDesignResolutionSize(lsSize.width * scale, lsSize.height * scale, kResolutionNoBorder);
    pEGLView->setDesignResolutionSize(480, 320, kResolutionShowAll);
     
    // create a scene. it's an autorelease object
    CCScene *pScene = MainScene::scene();

    // run
    pDirector->runWithScene(pScene);

    return true;
}

// This function will be called when the app is inactive. When comes a phone call,it's be invoked too
void AppDelegate::applicationDidEnterBackground() {
    CCDirector::sharedDirector()->stopAnimation();

    // if you use SimpleAudioEngine, it must be pause
    // SimpleAudioEngine::sharedEngine()->pauseBackgroundMusic();
}

// this function will be called when the app is active again
void AppDelegate::applicationWillEnterForeground() {
    CCDirector::sharedDirector()->startAnimation();

    // if you use SimpleAudioEngine, it must resume here
    // SimpleAudioEngine::sharedEngine()->resumeBackgroundMusic();
}
