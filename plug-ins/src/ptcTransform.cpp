#include "ptcNode.h"

#include <maya/MTypeId.h> 
#include <maya/MGlobal.h>

#include <maya/MSelectionList.h>
#include <maya/MPlugArray.h>

#include <maya/MItSelectionList.h>

#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MFnArrayAttrsData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnGenericAttribute.h>
// #include <maya/MFnData.h>
// #include <maya/MFnVectorArrayData.h>
// #include <maya/MFnCompoundAttribute.h>
// #include <maya/MFnComponentListData.h>

#include <maya/MArrayDataHandle.h>
#include <maya/MArrayDataBuilder.h>
#include <maya/MDataHandle.h>

#include <maya/MPoint.h>
#include <maya/MPointArray.h>

// #include <QtWidgets/QPushButton>

MTypeId ptcNode::id( 0x80028 );
MString ptcNode::drawRegistrantId( "ptcNodePlugin ");
MString ptcNode::drawDbClassification( "drawdb/geometry/ptcNode ");

// input attributes
MObject ptcNode::inMesh;

// node attributes
MObject ptcNode::aNumSamples;
MObject ptcNode::aNumInstances;
MObject ptcNode::aEmitRequest;
MObject ptcNode::aPointVisibility;
MObject ptcNode::aDisplaySize;
MObject ptcNode::aBrushRadius;

// output attributes
MObject ptcNode::instanceData;



// ptcNode::ptcNode() {}
// ptcNode::~ptcNode() {}


void* ptcNode::creator()
{
    return new ptcNode();
}

MStatus ptcNode::initialize()
{

    MStatus status = MS::kSuccess;

    MFnNumericAttribute numericAttrFn;
    MFnTypedAttribute typedAttrFn;
    MFnGenericAttribute genericAttrFn;

    // create generic output attribute
    instanceData = genericAttrFn.create("instanceData", "instanceData", &status );
    // make sure the generic attribute accepts the right data type
    status = genericAttrFn.addDataAccept( MFnArrayAttrsData::kDynArrayAttrs );
    genericAttrFn.setReadable( true );
    genericAttrFn.setWritable( true );
    genericAttrFn.setStorable( true ); // kDynArrayAttrs are not storeable
    genericAttrFn.setKeyable( false );
    status = addAttribute( instanceData );

    // input attributes
    aEmitRequest = numericAttrFn.create( "emit", "emit", MFnNumericData::kBoolean, 0 &status);
    numericAttrFn.setReadable( true );
    numericAttrFn.setWritable( true );
    numericAttrFn.setKeyable( false  );
    numericAttrFn.setHidden( false  );
    status = addAttribute( aEmitRequest );

    // node addributes
    aNumSamples = numericAttrFn.create( "numSamples", "numSamples", MFnNumericData::kInt, 0, &status );
    status = addAttribute( aNumSamples );

    aNumInstances = numericAttrFn.create( "numInstances", "numInstances", MFnNumericData::kInt, 0, &status );
    numericAttrFn.setDefault( 1 );
    numericAttrFn.setMin( 1 );
    status = addAttribute( aNumInstances );

    aPointVisibility = numericAttrFn.create( "pointVisibility", "pointVisibility", MFnNumericData::kBoolean, 0, &status );
    numericAttrFn.setDefault( true );
    status = addAttribute( aPointVisibility );

    aDisplaySize = numericAttrFn.create( "displaySize", "displaySize", MFnNumericData::kDouble, 0, &status );
    numericAttrFn.setDefault( 2.0 );
    numericAttrFn.setMin( 1.0 );
    status = addAttribute( aDisplaySize );

    aBrushRadius = numericAttrFn.create( "brushRadius", "brushRadiu", MFnNumericData::kDouble, 0, &status );
    numericAttrFn.setDefault( 2.0 );
    numericAttrFn.setMin( 1.0 );
    status = addAttribute( aBrushRadius );

    inMesh = typedAttrFn.create("inMesh", "inMesh", MFnMeshData::kMesh);
    typedAttrFn.setWritable( true );
    numericAttrFn.setHidden( false  );
    typedAttrFn.setReadable( false );
    typedAttrFn.setStorable( false );
    status = addAttribute( inMesh );

    status = attributeAffects(aEmitRequest, instanceData);

    CHECK_MSTATUS( status );
	return( status );
}

void ptcNode::draw( M3dView & view, const MDagPath & path,
                             M3dView::DisplayStyle style,
                             M3dView::DisplayStatus status )
{
    // MStatus status;
    MObject thisNode = thisMObject();

    // get position data
    MPlug instDataPlug ( thisNode, instanceData );
    MObject instDataAttr;
    instDataPlug.getValue( instDataAttr );
    MFnArrayAttrsData arrayAttrsFn(instDataAttr);
    MVectorArray position = arrayAttrsFn.getVectorData( "position" );

    // get point display size attr
    MPlug displaySizePlug ( thisNode, aDisplaySize );
    float pointSize;
    displaySizePlug.getValue( pointSize );

    // get point visibility
    MPlug displayVisibilityPlug ( thisNode, aPointVisibility );
    bool pointVisibility;
    displayVisibilityPlug.getValue( pointVisibility );

    // std::cout << pointVisibility << std::endl;

    if ( pointVisibility == 1 )
    {

        view.beginGL();

        glPushAttrib( GL_CURRENT_BIT );

        if ( status == M3dView::kActive )
            view.setDrawColor( 13, M3dView::kActiveColors );
        else
            view.setDrawColor( 13, M3dView::kDormantColors );

        glPointSize( pointSize );
        glBegin( GL_POINTS );

        for ( int i = 0; i < position.length(); i++ )
        {
            glVertex3f( position[i].x, position[i].y, position[i].z );
        }

        glEnd();

        view.endGL();
    }
}

// bool ptcNode::isBounded() const
// {
//     return false;
// }
//
// MBoundingBox ptcNode::boundingBox() const
// {
//     return MBoundingBox();
// }


MStatus ptcNode::compute( const MPlug& plug, MDataBlock& data )
{
    // MStatus status;
    MGlobal::displayInfo("FOO");
    MStatus status;

    if ( plug == instanceData )
        MGlobal::displayInfo("BAR");

        MDataHandle inMeshData = data.inputValue( inMesh, &status );
        MFnMesh meshFn( inMeshData.asMesh(), &status );
        // MFnMeshPolygon polyFn(inMeshData.asMesh(), &status );
        // MGlobal::displayInfo( inMeshData.asMesh() );
        MDataHandle inNumSamples = data.inputValue( aNumSamples, &status );
        int numSamples = inNumSamples.asInt();
        MDataHandle inNumInstances = data.inputValue( aNumInstances, &status );
        int numInstances = inNumInstances.asInt();

        MDataHandle outputData = data.outputValue( plug );
        bool t = true;
        bool f = false;

        MObject genericAttr;
        MObject attrsArrayObj;
        MFnArrayAttrsData arrayAttrsDataFn;

        if ( outputData.isGeneric( t, f ) )


            attrsArrayObj = arrayAttrsDataFn.create( &status );
            MVectorArray outPos = arrayAttrsDataFn.vectorArray( "position", &status );


            // genericAttr = genericAttrFn.create( &status ); // vectorArray("position", &status);
            // points = genericAttr.vectorArray("position", &status );

            for ( int i = 0; i < numSamples ; i++ )
            {
                double zero = 0.0;
                MPoint pnt(zero, i, zero);
                outPos.append(pnt);
            }

            outputData.set( attrsArrayObj );

    // int index = plug.logicalIndex( &status );
    // MArrayDataHandle hOutArray = data.outputArrayValue(instanceData, &status );
    // MArrayDataBuilder bOutArray = hOutArray.builder( &status );
    // MDataHandle hOut = bOutArray.addElement(index, &status );

    return( MS::kSuccess );
}


//
// DrawOverride
//

/*
ptcDrawOverride::ptcDrawOverride( const MObject& obj  )
: MHWRender::MPxDrawOverride( obj, ptcDrawOverride::draw )
{
    std::cout << "constructor" << std::endl;
}

ptcDrawOverride::~ptcDrawOverride()
{
}

MHWRender::DrawAPI ptcDrawOverride::supportedDrawAPIs() const
{
    return( MHWRender::kOpenGL | MHWRender::kDirectX11 | MHWRender::kOpenGLCoreProfile );
}

MUserData* ptcDrawOverride::prepareForDraw(
	const MDagPath& objPath,
	const MDagPath& cameraPath,
	const MHWRender::MFrameContext& frameContext,
	MUserData* oldData)
{
	ptcData* data = dynamic_cast<ptcData*>(oldData);
	if (!data)
	{
		data = new ptcData();
	}
    return( NULL );
}


void ptcDrawOverride::draw(const MHWRender::MDrawContext& context, const MUserData* data)
{
    cout << "I'M DRAWING NOW!!";
}
*/


//
// Brush Context
//

MObject brushContext::targetSurface;
M3dView brushContext::view;

brushContext::brushContext()
{
    // setTitleString ( "brushContext" );
}

void brushContext::toolOnSetup( MEvent& event )
{
    MStatus status;
    MGlobal::displayInfo( "brush setup" );

    // MObject manipObject;
    // brushManip::newManipulator( "brushManip", manipObject, &status );

    // brushManip::addManipulator( manipObject );




    MSelectionList slls;
    MGlobal::getActiveSelectionList( slls );
    // MDagPath nodePath;
    MObject node;
    // slls.getDagPath( 0, nodePath );
    slls.getDependNode( 0, node );
    // MGlobal::displayInfo( nodePath.fullPathName() );
    MFnDependencyNode dependNodeFn( node );

    if ( node.apiType() == MFn::kPluginLocatorNode )

        MPlug radiusPlug = dependNodeFn.findPlug( "brushRadius", &status );
        MPlug inMeshPlug = dependNodeFn.findPlug( "inMesh", &status );

        if ( !inMeshPlug.isNull() )
        {
            // get array of connected plugs, if there is a connection
            MPlugArray plugs;
            if ( inMeshPlug.connectedTo( plugs, true, false ) )
            {
                // get node from first plug, if it's of type mesh
                MObject inputNode = plugs[0].node();
                if ( inputNode.hasFn( MFn::kMesh ) )
                {
                    // the mesh node of "interest"
                    // this is the node we want to paint on
                    targetSurface = inputNode;
                }
            }

            // inMeshPlug.getValue( inMesh );
            // MGlobal::displayInfo( inMesh.apiTypeStr() ); // kMeshData
            // MGlobal::displayWarning( "ptcNode inMesh attribute not connected" );
            // return;
        }

    MString manipName ( "brushManip" );
    MObject manipObject;

    brushContext * ctrPtr = ( brushContext * ) this;
    brushManip* manipulator = ( brushManip* ) brushManip::newManipulator( manipName, manipObject );

    if ( NULL != manipulator )
    {
        ctrPtr -> addManipulator( manipObject );

        if ( !manipulator->connectToDependNode( node ) )
        {
            MGlobal::displayWarning("Error connecting manipulator to: " + dependNodeFn.name() );
        }

    }



    // MItSelectionList iter( slls, MFn::kInvalid, &status );

    // MObject obj;

    // if ( slls.length != 1 )

    // for ( ; !iter.isDone(); iter.next() )
    // {
    //     iter.getDagPath( path );
    //     MGlobal::displayInfo( path.fullPathName() );
    //     // MGlobal::displayInfo( path.apiType() );
    //
    //     iter.getDependNode( obj );
    //     MGlobal::displayInfo( obj.apiTypeStr() );
    // }

}

void brushContext::updateManipulators( void *data )
{
    MGlobal::displayInfo("updateManip");
}

MStatus brushContext::doPress( MEvent &event )
{
    MStatus status;
    MPoint pos = screenToWorld( event );
}

MStatus brushContext::doDrag( MEvent &event )
{
    MStatus status;
    MPoint pos = screenToWorld( event );
}

MStatus brushContext::doEnterRegion( MEvent &event )
{
    MGlobal::displayInfo("enterRegion");
}

MPoint brushContext::screenToWorld( MEvent &event )
{
    MStatus status;

    short x_pos, y_pos;
    status = event.getPosition( x_pos, y_pos );
    std::cout << x_pos << " " << y_pos << std::endl;

    view = view.active3dView( &status );
    MPoint worldPoint;
    MVector worldVector;
    view.viewToWorld( x_pos, y_pos, worldPoint, worldVector );

    std::cout << worldPoint << " " << worldVector << std::endl;

    // M3dView view.active3dView( &status );
    // view.getScreenPosition( x, y, &status );
    // std::cout << x << " " << y << std::endl;

    MPointArray intersections;
    double tolerance = 0.00000001;
    MFnMesh meshFn( targetSurface );
    meshFn.intersect( worldPoint, worldVector, intersections, tolerance, MSpace::kObject, NULL, &status);
    std::cout << "intersections" << intersections << std::endl;
    std::cout << "objtype" << targetSurface.apiTypeStr() << std::endl;

    MPoint pos;
    return pos;

}
// MStatus brushContext::doRelease( MEvent & event, MHWRender::MUIDrawManager& drawMgr, const MHWRender::MFrameContext& context)
// {
//     MStatus stat = doRelease( event ); // call VP1.0 version
//     printf("- VP2.0 version doRelease() called.\n");
//     return stat;
// }


//
// Brush Context Command
//


void *brushContextCmd::creator()
{
    return new brushContextCmd;
}

MPxContext *brushContextCmd::makeObj()
{
    return new brushContext();
}


//
// Brush Context Command
//


MTypeId brushManip::id( 0x8001d  ); // TODO get id

void *brushManip::creator()
{
    return new brushManip();
}

MStatus brushManip::initialize()
{
    MStatus status;
    status = MPxManipContainer::initialize();
    MGlobal::displayInfo("initManip");
    return status;
}

MStatus brushManip::connectToDependNode( const MObject &node )
{
    MStatus status;

    MFnDependencyNode nodeFn( node );
    std::cout << node.apiTypeStr() << std::endl;

    MPlug instanceDataPlug = nodeFn.findPlug( "instanceData", &status );
    // instanceDataPlug.
    MObject instDataObj;
    instanceDataPlug.getValue( instDataObj );
    std::cout << "FOO " << instDataObj.apiTypeStr() << std::endl;

    return MS::kSuccess;
}

void brushManip::draw(M3dView & view,
                     const MDagPath & path,
                     M3dView::DisplayStyle style,
                     M3dView::DisplayStatus status)
{
    MGlobal::displayInfo("drawing");
}

// MStatus brushManip::doPress()
// {
//     MGlobal::displayInfo("ManipPress");
// }
//
// MStatus brushManip::doDrag()
// {
//     MGlobal::displayInfo("ManipPress");
// }

//
// initialiazation / uninitialization
//
//


MStatus initializePlugin( MObject obj )
{ 
	MStatus   status;
	MFnPlugin plugin( obj, "Anno Schachner", "0.1", "Any");

	status = plugin.registerNode ( "ptcNode",
                                    ptcNode::id, 
                                    &ptcNode::creator,
                                    &ptcNode::initialize,
                                    MPxNode::kLocatorNode,
                                    &ptcNode::drawDbClassification );

	if (!status)
    {
		status.perror("registerNode");
		return( status );
	}

    status = plugin.registerContextCommand( "brushContext",
                                    brushContextCmd::creator );

	if (!status)
    {
		status.perror("registerNode");
		return( status );
	}

    status = plugin.registerNode( "brushManip",
                                    brushManip::id,
                                    brushManip::creator,
                                    brushManip::initialize,
                                    MPxNode::kManipContainer );

	if (!status)
    {
		status.perror("registerNode");
		return( status );
	}

    // status = MHWRender::MDrawRegistry::registerDrawOverrideCreator(
    //                                 ptcNode::drawDbClassification,
    //                                 ptcNode::drawRegistrantId,
    //                                 ptcDrawOverride::Creator );

	// if (!status)
    // {
	//     status.perror("registerNode");
	//     return( status );
	// }

	return( status );
}

MStatus uninitializePlugin( MObject obj)
{
	MStatus   status;
	MFnPlugin plugin( obj );

    // status = MHWRender::MDrawRegistry::deregisterDrawOverrideCreator(
    //                                 ptcNode::drawDbClassification,
    //                                 ptcNode::drawRegistrantId );

	// if (!status)
    // {
	//     status.perror("deregisterNode");
	//     return( status );
	// }
    //

    status = plugin.deregisterNode( ptcNode::id );

	if (!status)
    {
		status.perror( "deregisterNode" );
		return( status );
	}

    status = plugin.deregisterContextCommand( "brushContext" );

	if (!status)
    {
		status.perror( "deregisterNode" );
		return( status );
	}

    status = plugin.deregisterNode( brushManip::id );

	if (!status)
    {
		status.perror( "deregisterNode" );
		return( status );
	}

	return( status );
}



